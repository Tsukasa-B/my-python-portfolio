import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, RigidObjectCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass
from isaaclab.sensors import ContactSensorCfg

from .actions.torque import TorqueActionController

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" #Path(__file__)このファイルのある場所をオブジェクトでとる．resolve()絶対パスにして迷子にならない．parents[2]/"assets"２つ上の階層のassetsフォルダに入る
ROBOT_USD = str(ASSETS_DIR / "porcaro.usd")  #命名したASSETS_DIRのなかにあるusdファイルを取得し命名
DRUM_USD  = str(ASSETS_DIR / "sneadrum.usd")
DRUMSTAND_USD  = str(ASSETS_DIR / "sneadrumstand.usd")

# --- ロボットの設定 ---
ROBOT_CFG = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",  # /World/envs/env_.* の部分は省略可能
    spawn=sim_utils.UsdFileCfg(
        usd_path=ROBOT_USD,
    ),
    # ここにロボットのアクチュエータ設定を追加します (例)
    actuators = {
        "wrist": ImplicitActuatorCfg(
            joint_names_expr=[r"Base_link_Wrist_joint"],#rはrow string \がでたときに正規表現として読み込むためのもの
            stiffness=0,   # 例：必要なら上書き
            damping=0.02,
            effort_limit=500.0,
        ),
        "grip": ImplicitActuatorCfg(
            joint_names_expr=[r"Hand_link_Grip_joint"],
            stiffness=0,   # 例
            damping=0.02,
            effort_limit=500.0,
    ),
    },
)

# --- ドラムの設定 ---
DRUM_CFG = RigidObjectCfg(
    prim_path="{ENV_REGEX_NS}/DrumStand/Drum",
    parent="{ENV_REGEX_NS}/DrumStand/StandArm_link",
    spawn=sim_utils.UsdFileCfg(
        usd_path=DRUM_USD,
        init_state=sim_utils.AssetCfg.InitialStateCfg(
            pos=(0.0, 0.0, 0.1),
            rot=(1.0, 0.0, 0.0, 0.0)
        ),
    ),
)


# --- ドラムスタンドの設定 ---
DRUMSTAND_CFG = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/DrumStand",
    spawn=sim_utils.UsdFileCfg(
        usd_path=DRUMSTAND_USD,
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            fix_root=True
        )
    ),
    # こちらも関節を固定
    actuators={
        "freeze_joints": ImplicitActuatorCfg(
            joint_names_expr=[".*"],
            stiffness=1.0e6,
            damping=1.0e5,
        )
    },

    children={
        "drum": DRUM_CFG
    }
)





@configclass
class PorcaroRLEnvCfg(DirectRLEnvCfg):
    
    def __init__(self, cfg: PorcaroRLEnvCfg, **kwargs):
        super().__init__(cfg, **kwargs)

        dt_ctrl = self.cfg.sim.dt * self.cfg.decimation

        self.action_controller = TorqueActionController(
            dt_ctrl=dt_ctrl,
            r=0.014, L=0.150,
            Pmax=0.6,
        )

        # --- 2. 関節IDの取得 ---
        # コントローラがどの関節を操作するかをIDで覚えておく
        wrist_ids, _ = self.robot.find_joints(r"Base_link_Wrist_joint")
        grip_ids, _ = self.robot.find_joints(r"Hand_link_Grip_joint")
        self._wrist_id = wrist_ids[0]
        self._grip_id = grip_ids[0]


    def _reset_idx(self, env_ids: torch.Tensor):
        """特定環境IDのリセット"""
        # 環境がリセットされる際にコントローラもリセットする
        if env_ids is None:
            n_envs = self.num_envs
        else:
            n_envs = len(env_ids)
        self.action_controller.reset(n_envs, self.device)
        # (他のリセット処理...)

    # --- トルク計算のインスタンス化とメソッド作成 ---
    def _pre_physics_step(self, actions: torch.Tensor):
        """物理シミュレーションの直前に呼ばれる"""
        # エージェントからのアクションを[-1, 1]の範囲にクリップして保持
        self.actions = actions.clamp(-1.0, 1.0)


    def _apply_action(self):
        """保持されたアクションを適用する"""
        # --- 3. コントローラを実行してトルクを計算・適用 ---
        self.action_controller.apply(
            actions=self.actions,
            q=self.robot.data.joint_pos, # 現在の関節角度を渡す
            robot=self.robot, # robotオブジェクトを渡し、トルクを直接設定させる
            joint_ids=(self._wrist_id, self._grip_id)
        )   
    # ----------------------------------------------

    
    # env
    # episode_length_s = 5.0
    # decimation = 4
    # action_scale = 1
    # action_space = 3
    # observation_space = 5
    # state_space = 0

    # simulation 
    sim: SimulationCfg = SimulationCfg(
        dt=1 / 200,
        render_interval=1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,            
        )
    )
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    # contact_sensor: ContactSensorCfg = ContactSensorCfg(
    #     prim_path="/World/envs/env_.*/Robot/.*",  # Path to base_link in cloned envs
    #     history_length=5,
    #     update_period=0.005,  # Matches sim dt = 1/200
    #     track_air_time=True,  # Not needed for base
    # )

    # scene
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=1,
        env_spacing=3.0, # アセットが干渉しないように十分な距離を確保
        replicate_physics=True,


        robot=ROBOT_CFG,
        drum_stand=DRUMSTAND_CFG.replace(
            init_state = sim_utils.AssetCfg.InitialStateCfg(
                pos=(0.73871, 0.0, 0.0),
                rot=(1.0, 0.0, 0.0, 0.0),
            )
        )
    )



    # events
    # events: EventCfg = EventCfg()

    # robot


    #reward