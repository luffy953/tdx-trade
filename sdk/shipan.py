# -*- coding: utf-8 -*-
"""
通达信实盘高速量化交易网关 - Python SDK 客户端 (Zero-Dependency)
纯 Python 标准库编写，零 pip 依赖，开箱即用。
兼容 Python 3.7+ (Windows / Linux / macOS)。
"""

import json
import time
from typing import Any, Dict, List, Optional, Union
import urllib.error
import urllib.parse
import urllib.request


class ShipanError(Exception):
    """通达信实盘客户端异常基类"""
    pass


class ShipanClient:
    """通达信本地底层协议实盘网关客户端"""

    def __init__(self, host: str = "127.0.0.1", port: int = 19313, timeout: float = 5.0):
        """初始化通达信实盘网关客户端
        :param host: 本地或远程网关 IP，默认 '127.0.0.1'
        :param port: 网关监听端口，默认 19313
        :param timeout: 请求超时时间（秒），默认 5.0s
        """
        self.base_url = f"http://{host}:{port}".rstrip("/")
        self.timeout = timeout

    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Shipan-TDX-SDK/1.0.0",
        }
        req_data = None
        if data is not None:
            req_data = json.dumps(data, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"

        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        started = time.perf_counter()

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                content = response.read().decode("utf-8")
                elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
                try:
                    res_json = json.loads(content)
                    if isinstance(res_json, dict) and "networkRttMs" not in res_json:
                        res_json["networkRttMs"] = elapsed_ms
                    return res_json
                except Exception:
                    return {"ok": True, "raw": content, "networkRttMs": elapsed_ms}

        except urllib.error.HTTPError as e:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            try:
                err_data = json.loads(e.read().decode("utf-8"))
                if isinstance(err_data, dict):
                    err_data["httpStatus"] = e.code
                    err_data["networkRttMs"] = elapsed_ms
                    return err_data
            except Exception:
                pass
            return {"ok": False, "httpStatus": e.code, "error": str(e), "networkRttMs": elapsed_ms}

        except urllib.error.URLError as e:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            return {
                "ok": False,
                "error": "connection_failed",
                "message": f"无法连接到通达信本地网关 ({self.base_url})，请确认网关程序是否已启动: {e.reason}",
                "networkRttMs": elapsed_ms,
            }

        except Exception as e:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            return {"ok": False, "error": "unknown_exception", "message": str(e), "networkRttMs": elapsed_ms}

    # ==================== 状态检查 ====================

    def health(self) -> Dict[str, Any]:
        """获取网关健康状态、连接模式及通达信通信状态"""
        return self._request("GET", "/v1/health")

    def is_connected(self) -> bool:
        """检查网关是否处于就绪状态"""
        res = self.health()
        return bool(res.get("ok") and (res.get("status") == "ready" or res.get("connected") is True))

    # ==================== 核心交易接口 ====================

    def buy(
        self,
        symbol: Optional[str] = None,
        price: float = 0.0,
        amount: int = 0,
        code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """极速买入股票 / ETF
        :param symbol: 6位证券代码，如 '000001', '600519', '159915', '510300'
        :param price: 委托买入限价 (元)
        :param amount: 委托买入股数 (整百股，如 100)
        :param code: 别名参数，等同于 symbol
        """
        target_code = str(symbol or code or "").strip()
        payload = {
            "code": target_code,
            "symbol": target_code,
            "price": float(price),
            "amount": int(amount),
        }
        return self._request("POST", "/v1/buy", payload)

    def sell(
        self,
        symbol: Optional[str] = None,
        price: float = 0.0,
        amount: int = 0,
        code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """极速卖出股票 / ETF
        :param symbol: 6位证券代码，如 '000001', '600519', '159915', '510300'
        :param price: 委托卖出限价 (元)
        :param amount: 委托卖出股数 (整百股，如 100)
        :param code: 别名参数，等同于 symbol
        """
        target_code = str(symbol or code or "").strip()
        payload = {
            "code": target_code,
            "symbol": target_code,
            "price": float(price),
            "amount": int(amount),
        }
        return self._request("POST", "/v1/sell", payload)

    def cancel(
        self,
        entrust_no: Optional[str] = None,
        code: str = "",
        entrustNo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """撤销指定委托订单
        :param entrust_no: 委托合同编号 / 订单号
        :param code: 证券代码 (选填，部分券商撤单加速用)
        :param entrustNo: 别名参数，等同于 entrust_no
        """
        target_no = str(entrust_no or entrustNo or "").strip()
        payload = {
            "entrustNo": target_no,
            "entrust_no": target_no,
            "code": str(code).strip(),
        }
        return self._request("POST", "/v1/cancel", payload)

    # ==================== 核心查询接口 ====================

    def get_account(self) -> Dict[str, Any]:
        """查询资金账号、股东代码(沪深两市绑定账号)及当前通信模式"""
        return self._request("GET", "/v1/account")

    def get_balance(self) -> Dict[str, Any]:
        """查询账户资金资产 (总资产、可用资金、总市值等)"""
        return self._request("GET", "/v1/balance")

    def get_positions(self) -> Dict[str, Any]:
        """查询当前持仓明细 (股票代码、持仓数量、可用数量、参考市值等)"""
        return self._request("GET", "/v1/positions")

    def get_entrusts(self) -> Dict[str, Any]:
        """查询当日委托明细列表"""
        return self._request("GET", "/v1/entrusts")


# 别名兼容，无缝支持 TdxTrader 与 ShipanTrader
TdxTrader = ShipanClient
ShipanTrader = ShipanClient

__all__ = ["ShipanClient", "TdxTrader", "ShipanTrader", "ShipanError"]
