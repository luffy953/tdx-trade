# -*- coding: utf-8 -*-
"""
通达信实盘高速量化网关 - 资产、持仓与当日委托查询示例
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sdk.shipan import ShipanClient


def main():
    print("=" * 65)
    print("        通达信实盘高速网关 - 核心查询演示 (资金/持仓/委托)     ")
    print("=" * 65)

    client = ShipanClient(host="127.0.0.1", port=19313)

    # 1. 账户信息与股东代码
    print("📊 查询账户与股东代码 (GET /v1/account)...")
    account = client.get_account()
    print(f"   返回结果: {account}")

    # 2. 资金资产查询
    print("\n📊 查询账户资金状况 (GET /v1/balance)...")
    balance = client.get_balance()
    print(f"   返回结果: {balance}")

    # 3. 持仓股票查询
    print("\n📊 查询持仓明细 (GET /v1/positions)...")
    positions = client.get_positions()
    print(f"   返回结果: {positions}")

    # 4. 当日委托查询
    print("\n📊 查询当日委托记录 (GET /v1/entrusts)...")
    entrusts = client.get_entrusts()
    print(f"   返回结果: {entrusts}")
    print("=" * 65)


if __name__ == "__main__":
    main()
