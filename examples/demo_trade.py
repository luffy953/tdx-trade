# -*- coding: utf-8 -*-
"""
通达信实盘高速量化网关 - 实战交易与极速下单示例
"""
import sys
from pathlib import Path

# 添加上级目录以导入 sdk
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sdk.shipan import ShipanClient


def main():
    print("=" * 65)
    print("        通达信实盘高速网关 - 交易演示 (买入/卖出/撤单)       ")
    print("=" * 65)

    client = ShipanClient(host="127.0.0.1", port=19313)

    # 1. 检查网关与通达信连接状态
    health = client.health()
    if not health.get("ok"):
        print(f"❌ 网关连接失败: {health.get('message')}")
        return

    print("✅ 网关运行状态就绪:")
    print(f"   • 服务标识: {health.get('service')}")
    print(f"   • 运行模式: {health.get('mode', 'live')}")
    print(f"   • 资金账号: {health.get('account')}")
    print(f"   • 服务端口: {health.get('port', 19313)}")
    print("-" * 65)

    # 2. 模拟极速买入 (平安银行 000001)
    # 实盘建议：测试时可挂跌停价买入，验证链路而不成交
    print("🚀 发起极速买入指令: 000001 (平安银行) | 价格: 9.50 | 数量: 100 股...")
    buy_res = client.buy(symbol="000001", price=9.50, amount=100)
    print(f"   返回结果: {buy_res}")
    print(f"   底层耗时: {buy_res.get('elapsedMs', 0)} ms")

    entrust_no = buy_res.get("entrustNo") or "123456"

    # 3. 模拟极速卖出
    # 实盘建议：测试时可挂涨停价卖出
    print("\n🚀 发起极速卖出指令: 000001 (平安银行) | 价格: 15.00 | 数量: 100 股...")
    sell_res = client.sell(symbol="000001", price=15.00, amount=100)
    print(f"   返回结果: {sell_res}")
    print(f"   底层耗时: {sell_res.get('elapsedMs', 0)} ms")

    # 4. 模拟撤单
    print(f"\n🚀 发起撤单指令: 合同编号 {entrust_no}...")
    cancel_res = client.cancel(entrust_no=entrust_no, code="000001")
    print(f"   返回结果: {cancel_res}")
    print(f"   底层耗时: {cancel_res.get('elapsedMs', 0)} ms")
    print("=" * 65)


if __name__ == "__main__":
    main()
