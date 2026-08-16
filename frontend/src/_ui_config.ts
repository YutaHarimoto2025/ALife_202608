/** params/frontend_ui.yaml を読み込み、UI設定として型付きで公開する。 */
import { parse } from "yaml";

import _frontendUiYaml from "../../params/frontend_ui.yaml?raw";

type _UiConfig = {
  camera: {
    min_scale: number;
    max_scale: number;
    pan_step: number;
  };
  speed_multiplier_default: number;
  speed_multiplier_min: number;
  speed_multiplier_max: number;
  speed_multiplier_step: number;
  wall: {
    thickness: number;
  };
  show_particle_footprint: boolean;
  max_particle_footprint_points: number;
};

export const uiConfig = parse(_frontendUiYaml) as _UiConfig;
