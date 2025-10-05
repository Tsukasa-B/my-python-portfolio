# spown_check.py
#
# このスクリプトは強化学習のロジックを実行せず、
# env_cfg.pyで定義されたアセットをシミュレーション環境にスポーンするためだけのものです。
# これにより、アセットの初期位置や見た目をインタラクティブに確認・調整できます。

import torch
import isaaclab
from isaaclab.app import AppLauncher
from isaaclab.envs import BaseEnv
from isaaclab.sim import sim_utils

# あなたが作成した設定ファイルをインポートします
# ファイル名が 'env_cfg.py' であることを前提としています
from env_cfg import PorcaroRLEnvCfg


class DesignEnv(BaseEnv):
    """
    アセットのスポーンと可視化のみを行うシンプルな環境クラス。
    RLのロジック（観測、報酬、行動など）はすべて省略しています。
    """

    cfg: PorcaroRLEnvCfg  # 型ヒントとして設定クラスを指定

    def __init__(self, cfg: PorcaroRLEnvCfg, **kwargs):
        # 親クラス(BaseEnv)の初期化を呼び出します
        # これにより、cfg.sceneに基づいてアセットが自動的にスポーンされます
        super().__init__(cfg, **kwargs)

    def _setup_scene(self):
        # BaseEnvのセットアップを呼び出すことで、cfg.scene内の"robot"や"drum_stand"が
        # 自動的にシーンに追加されます。
        super()._setup_scene()
        # シーンを見やすくするために光源を追加します
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    # --- 以下はBaseEnvを継承する上で必要なダミーのメソッドです ---
    # --- 今回の目的（スポーンの確認）では中身は不要なので 'pass' とします ---

    def _pre_physics_step(self, actions):
        pass

    def _apply_action(self):
        pass

    def _get_observations(self) -> dict:
        return {}

    def _get_rewards(self) -> torch.Tensor:
        return torch.zeros(self.num_envs, device=self.device)

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        return (torch.zeros(self.num_envs, device=self.device, dtype=torch.bool),
                torch.zeros(self.num_envs, device=self.device, dtype=torch.bool))

    def _reset_idx(self, env_ids: torch.Tensor | None):
        pass


def main():
    """環境を起動し、シミュレーションを実行します。"""
    # Isaac Simアプリケーションを起動します
    # headless=Falseにすることで、GUIウィンドウが表示されます
    app_launcher = AppLauncher(headless=False)
    simulation_app = app_launcher.app

    # 設定ファイルをインスタンス化
    cfg = PorcaroRLEnvCfg()

    # 設計用の環境クラスをインスタンス化
    env = DesignEnv(cfg=cfg)

    # シミュレーションが実行されている間、ループを回します
    while simulation_app.is_running():
        # 推論モードで実行（今回は何もしませんが、定型句として）
        with torch.inference_mode():
            # 環境を1ステップ進めます
            # これにより物理演算とレンダリングが行われます
            env.step(None)

    # シミュレーションを終了
    env.close()


if __name__ == "__main__":
    main()