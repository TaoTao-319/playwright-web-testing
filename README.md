# Playwright Web UI 测试

使用 Python、pytest 与 Playwright 测试 Sauce Demo 核心购物流程，采用页面对象、独立上下文、参数化、失败截图与追踪。主业务集 22 条，基础控件练习 15 条，验收工具另有 7 项检查。

## 安装与执行

需要 Python 3.14。创建并激活虚拟环境后执行：

```bash
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest
python scripts/validate_project.py
```

Linux 安装浏览器时使用 `python -m playwright install --with-deps chromium`。Windows 可双击 `run-tests.bat` 运行并打开报告，`open-report.bat` 只查看已有结果。

## 模块

| 目录 | 职责 |
|---|---|
| pages | 登录、商品、购物车和结算页面操作 |
| tests | 主业务场景与断言 |
| test_data | 预期数据和文件样本 |
| practice/controls | 菜鸟教程下拉框、复选框、文件选择、显示隐藏和 AJAX，单独执行 |
| failure_lab | 显式故障演练，与默认测试隔离 |
| checks | 验收逻辑单元检查 |
| scripts | 回归、独立用例、故障与恢复的完整验收 |

控件练习执行 `python -m pytest practice/controls`；验收逻辑检查执行 `python -m pytest checks -o addopts='' -q`。控件使用独立外部站点，不计入 22 条业务回归。

## 结果与 CI

用浏览器打开 `reports/report.html`。失败截图和 trace 位于 `test-results`；全部通过时没有失败截图属于正常情况。`python -m playwright show-trace "trace.zip路径"` 可检查操作、页面快照与网络。

完整验收要求主回归和独立购买场景通过，故障演练恰好因指定标题断言失败，再恢复正确预期通过；环境异常或其他失败不能算演练成功。

GitHub Actions 在 push、Pull Request 和手动运行时执行完整验收，保留报告及失败证据 14 天。手动勾选 `demonstrate_failure` 可额外观察一次红色失败运行。业务测试访问公共演示站点；仅对首页瞬时连接故障重新打开一次，业务断言不自动重试。

## 验证记录

22 条业务测试、15 条控件测试、7 项验收检查通过；预期断言失败与恢复验证完成。[执行摘要](docs/verification.json) · [用例清单](docs/test-cases.csv) · [业务报告](examples/reports/report.html) · [控件报告](examples/reports/controls.html)
