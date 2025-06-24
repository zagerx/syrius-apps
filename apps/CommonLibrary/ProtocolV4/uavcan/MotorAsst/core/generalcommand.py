"""
通用命令执行模块
功能:
1. 统一命令参数解析
2. 构建DSDL请求
3. 执行命令并等待响应
"""

from typing import Any, Dict
import asyncio
import logging
from MotorAsst.config.configdrivers import DriverConfig
from MotorAsst.drivers.can.transport import CANNodeService

class CommandExecutor:
    def __init__(self, node_service: CANNodeService, commands_config: Dict[str, Any]):
        self.node = node_service
        self.config = commands_config
        self._logger = logging.getLogger(__name__)

    async def send(self, command_name: str, params: Dict) -> bool:
        """统一命令发送接口"""
        try:
            config = self.config[command_name]
            client = self.node.create_client(
                config.data_type,
                config.server_node_id,
                config.port
            )
            
            request = self._build_request(command_name, params)
            response = await asyncio.wait_for(
                client.call(request),
                timeout=config.timeout
            )
            return bool(response)

        except Exception as e:
            self._logger.error(f"命令执行失败 {command_name}: {e}")
            return False
        except asyncio.TimeoutError:
            self._logger.warning(f"命令 {command_name} 超时")
            return False        
        except Exception as e:
            self._logger.error(f"命令 {command_name} 执行失败: {e}")
            return False
        finally:
            if client:
                client.close()

    def _build_request(self, command_name: str, params: Dict) -> Any:
        """构建DSDL请求对象"""
        if command_name == "SetVelocity":
            return DriverConfig.build_velocity_request(params)
        elif command_name == "SetMode":
            from uavcan.si.unit.velocity import Scalar_1_0 as VelocityScalar
            from uavcan.si.unit.acceleration import Scalar_1_0 as AccelerationScalar
            return self.config[command_name].data_type.Request(
                mode=params["mode"],
                max_velocity=VelocityScalar(params["max_velocity"]),
                acceleration=AccelerationScalar(params["acceleration"]),
                deceleration=AccelerationScalar(params["deceleration"])
            )
        return self.config[command_name].data_type.Request(**params)
