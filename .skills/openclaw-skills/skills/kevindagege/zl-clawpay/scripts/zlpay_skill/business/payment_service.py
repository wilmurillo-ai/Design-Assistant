# -*- coding: utf-8 -*-
"""
支付服务模块
"""

import io
import base64
import qrcode
from typing import Dict, Any, Optional
from ..config import Config
from ..core.secure_client import SecureClient
from ..exceptions import APIError, SecurityError

class PaymentService:
    """支付服务 - 处理支付相关业务逻辑"""
    
    def __init__(self, skill, memory):
        """
        初始化支付服务
        
        Args:
            skill: ZLPaySkill 实例，用于调用 api_call
            memory: 记忆管理器
        """
        self.skill = skill
        self.memory = memory
    
    def create_qr_code(self, session_id=None, interface_id=None, params=None, body=None):
        # type: (Optional[str], Optional[str], Optional[Dict], Optional[Dict]) -> Dict[str, Any]
        """
        生成收款码流程
        
        Args:
            session_id: 会话ID
            interface_id: 接口编码（如 C00004）
            params: URL参数
            body: 请求体，包含 amount, description 等业务参数
            
        Returns:
            收款码结果（包含 URL、seqId 和可选的图片）
        """
        if body is None:
            body = {}
        
        # 优先从 memory 获取已保存的 api_key，否则从 Config 读取
        api_key = self.memory.recall_api_key()
        if not api_key:
            api_key = Config.get_api_key(memory=self.memory)
        
        # 从 memory 获取 subWalletId（绑定后场景）
        sub_wallet_id = self.memory.get_wallet()
        if not sub_wallet_id:
            raise ValueError(u"未绑定子钱包，请先执行 bind_sub_wallet")
        
        amount = body.get('amount')
        description = body.get('description') or body.get('remark')
        
        if not amount:
            raise ValueError(u"缺少 amount 参数")
        
        # 创建 SecureClient（延迟初始化，使用已绑定的 api_key）
        client = SecureClient(lazy_init=True)

        # 构造请求参数
        request_data = {
            "subWalletId": sub_wallet_id,
            "amount": float(amount)
        }
        if description:
            request_data["description"] = description
        
        return_image = body.get('return_image', True)
        
        # 调用 API（secure_request 已统一注入 _seq_id）
        try:
            response = client.with_api_key(api_key).secure_request(
                method="POST",
                endpoint="/post/claw/create-qr-code",
                interface_id=interface_id,
                body=request_data
            )
            
            # 如果需要返回图片，将 URL 渲染成二维码
            payment_url = response.get("resData", {}).get("qrCode")
            if return_image and payment_url:
                qr_image_base64 = self._render_qr_code(payment_url)
                response["resData"]["qr_image"] = qr_image_base64
            
            return response
            
        except (APIError, SecurityError, requests.RequestException) as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _render_qr_code(self, url):
        # type: (str) -> str
        """
        将 URL 渲染成二维码图片
        
        Args:
            url: 支付链接
            
        Returns:
            Base64 编码的二维码图片
        """
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # 创建图片
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为 Base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        
        return img_base64
    
    
