import argparse
import csv
import importlib.metadata
import json
import platform
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_run(name, report_dir=None):
    report_dir = report_dir or ROOT / "reports"
    path = report_dir / f"{name}.xml"
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    cases = list(root.iter("testcase"))
    counts = {key: sum(int(s.get(key, 0)) for s in suites)
              for key in ("tests", "failures", "errors", "skipped")}
    counts["passed"] = counts["tests"] - counts["failures"] - counts["errors"] - counts["skipped"]
    counts["duration_seconds"] = round(sum(float(s.get("time", 0)) for s in suites), 3)
    counts["report"] = (report_dir / f"{name if name != 'results' else 'report'}.html").relative_to(ROOT).as_posix()
    counts["cases"] = [{"name": c.get("name"), "module": c.get("classname"),
                        "message": "\n".join((n.text or "") + " " + n.get("message", "")
                                             for n in c if n.tag in {"failure", "error"}),
                        "status": "failed" if c.find("failure") is not None else
                                  "error" if c.find("error") is not None else
                                  "skipped" if c.find("skipped") is not None else "passed"}
                       for c in cases]
    return counts


CASES = {
    "test_login_success": ("正常登录", "未登录", "填写正确演示账号密码并登录", "进入商品页并显示 Products 和商品"),
    "test_login_rejected": ("登录输入校验", "未登录", "分别提交错误密码、受限账号、空用户名、空密码", "对应错误提示出现，保留登录页"),
    "test_login_retry_after_wrong_password": ("纠正错误密码", "未登录", "错误密码登录后不刷新，改用正确密码", "进入商品页，错误提示消失"),
    "test_inventory_product_information": ("商品信息", "独立登录", "读取商品数量和背包、车灯价格", "共 6 件；价格 29.99、9.99"),
    "test_sort_price_low_to_high": ("价格升序", "独立登录", "选择价格从低到高并读取全部价格", "共 6 件，数字价格升序"),
    "test_sort_price_high_to_low": ("价格降序", "独立登录", "选择价格从高到低并读取全部价格", "共 6 件，数字价格降序"),
    "test_sort_name_descending_and_restore": ("名称排序", "独立登录", "先选择 Z 到 A，再选择 A 到 Z", "商品名称先降序后升序"),
    "test_add_one_product": ("单件加购", "独立登录，空购物车", "添加背包并打开购物车", "数量为 1，名称、价格和数量正确"),
    "test_add_two_products": ("多件加购", "独立登录，空购物车", "添加背包与车灯，打开购物车", "数量为 2，商品名称与价格正确"),
    "test_cart_keeps_products_after_returning_to_inventory": ("购物车保留", "独立登录", "添加两件商品，进购物车，再返回商品页并重新进入", "商品和数量保持不变"),
    "test_remove_one_keeps_other": ("移除一件", "独立登录，自行添加两件商品", "移除背包并返回商品页", "车灯保留，徽标为 1，背包可重新添加"),
    "test_readd_product_after_removing": ("移除再添加", "独立登录，自行添加两件商品", "移除背包，返回商品页并重新添加", "恢复两件商品，每件数量 1"),
    "test_remove_all_products": ("清空购物车", "独立登录，自行添加背包", "从购物车移除背包", "商品为空，数量徽标消失"),
    "test_logout_returns_to_login": ("退出登录", "独立登录", "菜单中点击退出", "返回登录页，输入框与按钮可见"),
    "test_checkout_subtotal": ("订单预览与取消", "独立登录，自行添加背包和车灯", "提交完整结算信息，核对预览后取消", "商品正确，小计 39.98，取消后返回商品页"),
    "test_checkout_required_fields": ("结算必填校验", "独立登录，自行添加背包并进入结算", "分别留空名字、姓氏、邮编并继续", "对应必填提示出现，停留在信息页"),
    "test_complete_purchase": ("完整购买", "独立登录，自行添加背包和车灯", "填写结算信息，核对预览，完成订单，返回购物车", "商品和小计正确，出现完成提示，购物车清空"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_expected_failure(run):
    require(run["tests"] == 1 and run["failures"] == 1 and run["errors"] == 0
            and run["skipped"] == 0, "故障演练必须恰好出现一条断言失败，不能是环境错误或跳过")
    require(len(run["cases"]) == 1 and "Wrong Products Title" in run["cases"][0]["message"]
            and "Actual value: Products" in run["cases"][0]["message"],
            "故障原因与预期不符，不能将其他失败当作演练成功")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, default=Path("reports"))
    parser.add_argument("--artifact-dir", type=Path, default=Path("test-results"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("evidence"))
    args = parser.parse_args()
    report_dir = (ROOT / args.report_dir).resolve()
    artifact_dir = (ROOT / args.artifact_dir).resolve()
    evidence_dir = (ROOT / args.evidence_dir).resolve()
    for folder in (report_dir, artifact_dir, evidence_dir):
        require(folder.is_relative_to(ROOT), "输出目录必须位于项目内")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    runs = {name: read_run(name, report_dir) for name in
            ("results", "failure-demo", "recovered", "independent")}
    for name in ("results", "recovered", "independent"):
        require(runs[name]["tests"] > 0 and runs[name]["passed"] == runs[name]["tests"],
                f"{name} 有失败、错误或跳过：{runs[name]}")
    require(runs["results"]["tests"] == 22, "核心回归集应收集并执行 22 条用例")
    verify_expected_failure(runs["failure-demo"])
    images = sorted((artifact_dir / "failure-demo").rglob("*.png"))
    traces = sorted((artifact_dir / "failure-demo").rglob("trace.zip"))
    require(images and traces, "故障演练缺少截图或追踪文件")
    for path in images:
        require(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), "截图不是有效的 PNG 文件")
    trace_errors = []
    for path in traces:
        with zipfile.ZipFile(path) as archive:
            require(archive.testzip() is None, "追踪压缩包损坏")
            for name in archive.namelist():
                if name.endswith(".trace"):
                    calls = {}
                    for line in archive.read(name).decode("utf-8").splitlines():
                        event = json.loads(line)
                        if event.get("type") == "before":
                            calls[event.get("callId")] = event
                        if event.get("error"):
                            trace_errors.append({"call": calls.get(event.get("callId")),
                                                 "error": event["error"]})
    require(any("Wrong Products Title" in str(error) for error in trace_errors), "追踪文件未记录预期断言")
    report = {
        "verified_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "python": platform.python_version(),
        "dependencies": {p: importlib.metadata.version(p) for p in
                         ("playwright", "pytest", "pytest-playwright", "pytest-html")},
        "runs": runs,
        "failure_investigation": {
            "cause": "演练故意使用错误的商品页标题预期，属于脚本断言错误",
            "expected": "Wrong Products Title", "actual": "Products",
            "recovery": "移除 --failure-demo 开关，恢复正确预期并单独执行通过",
            "screenshots": [p.relative_to(ROOT).as_posix() for p in images],
            "traces": [p.relative_to(ROOT).as_posix() for p in traces],
            "trace_errors": trace_errors,
        },
    }
    (evidence_dir / "validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    with (evidence_dir / "test-cases.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["场景", "前置条件", "具体操作", "预期结果", "脚本", "执行结果"])
        for case in runs["results"]["cases"]:
            function = case["name"].split("[")[0]
            title, precondition, steps, expected = CASES[function]
            parameter_details = {
                "wrong-password": ("输入 standard_user 和 wrong_password，点击登录", "显示账号或密码不匹配，停留登录页"),
                "locked-account": ("输入 locked_out_user 和 secret_sauce，点击登录", "显示账号已锁定，停留登录页"),
                "empty-username": ("用户名留空，输入 secret_sauce，点击登录", "显示 Username is required，停留登录页"),
                "empty-password": ("输入 standard_user，密码留空，点击登录", "显示 Password is required，停留登录页"),
                "missing-first-name": ("名字留空，姓氏填 Learner，邮编填 100000，点击继续", "显示 First Name is required，停留结算信息页"),
                "missing-last-name": ("名字填 Test，姓氏留空，邮编填 100000，点击继续", "显示 Last Name is required，停留结算信息页"),
                "missing-postal-code": ("名字填 Test，姓氏填 Learner，邮编留空，点击继续", "显示 Postal Code is required，停留结算信息页"),
            }
            for parameter, detail in parameter_details.items():
                if case["name"].endswith(parameter + "]"):
                    steps, expected = detail
                    break
            writer.writerow([title + " " + case["name"], precondition, steps, expected,
                             case["module"].replace(".", "/") + ".py::" + case["name"], case["status"]])
    print(json.dumps({name: {k: v for k, v in run.items() if k != "cases"}
                      for name, run in runs.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
