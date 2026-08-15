# 2. 拡張可能な要素

以下は、今後 sandbox に追加可能な要素の候補である。

最初からすべて実装せず、単純な feed-forward agent を基準として段階的に追加する。

---

## Sensor / receptor

- **視界距離**
  - 遠くまで見える個体ほど情報量が増える。
  - 高性能ほど energy cost を大きくできる。

- **視野角**
  - 前方だけを見る、広角で見る、360 度見るなどを遺伝形質にできる。

- **視覚解像度**
  - ray 数や receptor 数を変化させる。
  - 高解像度ほど計算・維持コストを高くする。

- **sensor 配置**
  - receptor の向きや配置自体を進化可能にする。

- **対象別 receptor**
  - food、predator、prey、obstacle、同種個体などを別 channel として入力する。

- **sensor noise**
  - sensing にノイズを与える。
  - 高精度 sensor は高コストという trade-off を作れる。

---

## Brain

- **固定 Fully Connected Neural Network**
  - 初期実装。
  - 現在の sensor input だけから action を決定する反射型 agent。

- **NN weight evolution**
  - weight を genome に持たせ、GA で mutation / crossover する。

- **NN topology evolution**
  - neuron / edge の追加・削除自体を遺伝的操作にする。
  - NEAT 的な方向。

- **brain size cost**
  - neuron 数、edge 数が多いほど維持 energy cost を増やす。

- **activity cost**
  - NN の大きさだけでなく、実際の activation 量に応じて energy を消費させる。

- **computation delay**
  - 大きな brain は reaction が遅い、といった trade-off を導入する。

- **RNN**
  - 将来追加。
  - hidden state により過去の観測を記憶できる。
  - 初期段階では使用しない。

- **CTRNN**
  - Continuous-Time Recurrent Neural Network。
  - neuron に時定数を持たせ、振動や周期運動などの dynamics を表現できる。

---

## Action / actuator

- **最大推力**
  - 高推力ほど高加速。
  - 大きな energy cost を持たせる。

- **最大速度**
  - agent ごとの `vmax` を遺伝形質にできる。
  - world 側の絶対上限以下に制限する。

- **旋回性能**
  - angular acceleration や最大旋回速度を遺伝させる。

- **body mass**
  - 加速や慣性に影響する。

- **drag**
  - 速度比例抵抗などを導入する。

- **movement energy**
  - 推力、速度、加速度などに応じて energy を消費させる。

---

## Body / morphology

- **半径**
  - body size を遺伝形質にする。
  - 大型化による速度、energy、捕食能力などへの影響を設定できる。

- **mass**
  - body size と独立または連動して進化させる。

- **基礎代謝**
  - 高性能な身体ほど idle 状態でも energy を消費する。

- **sensor / brain / motor の統合コスト**
  - body 全体の維持コストを構成要素から算出する。

---

## Energy / homeostasis

- **energy**
  - survival と reproduction の中心となる内部状態。

- **basal metabolism**
  - 生存しているだけで energy を消費する。

- **sensor cost**
  - 視覚性能などに応じた維持費。

- **brain cost**
  - neuron / edge 数や活動量に応じた維持費。

- **motor cost**
  - force や movement に応じた消費。

- **homeostasis**
  - energy、temperature、hunger などを適正範囲に維持することを行動原理にする。

- **明示的 reward を使わない設計**
  - food -> energy -> survival -> reproduction だけを環境ルールとして与える。
  - fitness を人間が直接定義しすぎない。

---

## Environment

- **food**
  - energy source。

- **resource regeneration**
  - food の再生成速度や空間分布を変更する。

- **obstacle**
  - static obstacle。
  - agent の移動や sensing を制限する。

- **potential field**
  - attraction / repulsion などを force として追加する。

- **spatially heterogeneous environment**
  - 場所によって resource、cost、危険度などを変化させる。

- **環境の時間変化**
  - resource 分布や危険領域などを時間変化させる。

---

## Interaction

- **predation**
  - predator と prey が一定距離以内に一定時間存在した場合に捕食成立。

- **attack**
  - proximity と action を条件に damage を与える。

- **mating**
  - 一定距離以内で繁殖条件を満たした pair が offspring を生成する。

- **resource harvesting**
  - food 近傍に一定時間いると resource を取得する。

- **communication**
  - nearby agent に signal を送る action / receptor を追加する。

- **contact duration**
  - proximity pair ごとに滞在時間を sparse に bookkeeping する。

---

## Genetic Algorithm

- **weight mutation**
  - NN weight に Gaussian noise などを加える。

- **crossover**
  - 親個体間で genome を組み合わせる。

- **selection**
  - reproduction 成功や survival によって自然に selection を発生させる。

- **mutation rate evolution**
  - mutation probability 自体を genome に含める。

- **mutation scale evolution**
  - mutation の大きさ `sigma` 自体を進化させる。

- **crossover tendency**
  - crossover しやすさ自体を遺伝形質にする。

- **self-adaptive evolution**
  - 「何が変化するか」だけでなく「どの程度変化しやすいか」も進化させる。

---

## Lifetime learning / RL

- **個体内 RL**
  - 個体が生存中の reward に応じて NN を更新する。

- **GA + RL**
  - GA が初期 weight や RL hyperparameter を進化させ、生涯中には RL で学習する。

- **learning rate evolution**
  - RL の learning rate を遺伝形質にする。

- **discount factor evolution**
  - reward discount などの学習特性を遺伝させる。

- **plasticity evolution**
  - NN の可塑性の強さや学習則そのものを genome に含める。

- **Hebbian plasticity**
  - pre/post neuron の活動から局所的に weight を変える学習則。

- **Baldwin effect**
  - 学習可能性が進化し、長期的には学習していた行動が先天的構造へ取り込まれる現象を観察する。

- **Lamarckian inheritance**
  - 生涯学習後の weight を offspring に継承する。

- **Darwinian inheritance**
  - 生涯学習結果は継承せず、出生時 genome のみを遺伝させる。

---

## Exploration / diversity

- **Novelty Search**
  - reward の高さではなく、行動が既存個体とどれだけ異なるかを selection criterion にする。

- **behavior descriptor**
  - 平均速度、探索範囲、旋回頻度、他個体との距離などで行動を記述する。

- **MAP-Elites**
  - 単一の最強個体ではなく、異なる behavioral niche ごとに優秀な個体を保存する。

- **diversity pressure**
  - population が一種類の戦略へ collapse しすぎないように diversity を維持する。

---

## Intrinsic motivation

- **curiosity**
  - 予測できなかった状態変化を内部 reward とする。

- **prediction error**
  - world model の予測誤差を exploration signal にする。

- **novel state exploration**
  - 訪問頻度の低い領域へ向かう動機を与える。

---

## World model

- **next-state prediction**
  - `state + action -> next state` を予測する NN を持つ。

- **internal simulation**
  - 予測した未来状態を使って action を選択する。

- **predictive agent**
  - 反射型 agent と比較し、内部モデルを持つことの利点を調べる。

---

## Coevolution

- **predator-prey**
  - 捕食者と獲物を同時に進化させる。

- **Red Queen dynamics**
  - 相手側の進化により selection pressure が継続的に変化する状況を作る。

- **competitive coevolution**
  - 同じ resource を奪い合う個体同士を進化させる。

- **cooperative evolution**
  - 個体間協力によって fitness が上がる環境を作る。

---

## Cost / trade-off

基本思想として、性能を上げれば必ず何らかの cost が増えるようにする。

例:

- 長距離視覚 -> sensor cost 増加
- 高解像度視覚 -> computation cost 増加
- 高速移動 -> motor / basal cost 増加
- 大型 body -> maintenance cost 増加
- 大型 brain -> brain cost 増加
- 多数の NN edge -> maintenance / activity cost 増加
- 高い plasticity -> learning cost や instability を増やす

これにより「すべての性能を最大化する個体」が自動的に最適になることを避ける。

---

## Genome の拡張例

初期:

```text
Genome
|
+-- NN weights
```

次段階:

```text
Genome
|
+-- sensor parameters
+-- NN weights
+-- motor parameters
+-- mutation parameters
```

さらに拡張:

```text
Genome
|
+-- morphology
+-- sensors
+-- brain topology
+-- brain weights
+-- plasticity
+-- motor
+-- metabolism
+-- mutation strategy
+-- reproduction strategy
```

最終的には身体・感覚・脳・学習則・進化しやすさ自体が共進化する系まで拡張できる。


---

## BioSim4 から参考になる発想

David R. Miller の `biosim4` は、2D 空間上の個体に小さな neural circuit を持たせ、世代交代によって行動回路を進化させる biological evolution simulator である。

今回の sandbox と特に関連が深い発想を以下に整理する。

### Gene = neural connection

- 1 gene がほぼ 1 本の NN edge を表す。
- gene は概念的に以下を持つ。
  - source type: sensor / internal neuron
  - source index
  - sink type: internal neuron / action
  - sink index
  - weight
- Genome はこの gene の列であり、Genome から出生時に neural network を組み立てる。
- 固定した layer 構造を持たず、sensor -> action の直接接続も neuron を介した接続も可能。
- NN topology と weight を同じ遺伝表現で進化させられる簡潔な方式として参考になる。

### Genotype と phenotype の分離

- genome に記録された接続をそのまま実行するのではなく、出生時に実際の neural network を構築する。
- 結果として、遺伝子表現と実際に働く brain を分離できる。
- 将来的には dead connection、neutral gene、発現条件などを持たせる余地がある。

### 生涯学習を行わない純粋な neuroevolution

- 個体の brain は出生時に確定する。
- 生涯中に backpropagation や RL による weight 更新を行わない。
- 行動適応は世代間の mutation / recombination / selection のみで発生する。
- 「本能だけで何が進化するか」を調べる初期実験として参考になる。

### 自由な neural topology

- sensor、internal neuron、action 間の接続は layer に拘束されない。
- sensor -> action の単純な反射回路から、internal neuron を介した複雑な回路まで同じ genome 表現で扱える。
- BioSim4 自体は neuron state を step 間で保持できるため recurrent 的な回路も作れる。
- 今回の初期版では recurrent connection を禁止し、後から解禁する比較実験が考えられる。

### 意味を持つ低次元 sensor

BioSim4 は画像入力ではなく、環境や個体状態を直接表す少数の sensor を用いる。

実装例:

- `Lx`, `Ly`
  - world 内の正規化 X/Y 座標。
- `BD`, `BDx`, `BDy`
  - 最寄り境界までの距離、および X/Y 軸方向の境界距離。
  - 現在の main branch では mnemonic が `ED`, `EDx`, `EDy` になっている。
- `LMx`, `LMy`
  - 直前の移動方向の X/Y 成分。
- `Age`
  - 世代内での個体年齢。
- `Rnd`
  - 0..1 の乱数。
  - neural circuit 内の確率的行動源として使える。
- `Osc`
  - 個体内部 oscillator の周期信号。
  - RNN がなくても周期行動を生成できる。
- `Pop`
  - 周辺の population density。
- `Pfd`
  - 直前の進行方向を軸とした、前後方向の population 偏り。
- `Plr`
  - 進行方向に直交する左右方向の population 偏り。
- `LPf`
  - 前方 long probe による、最寄り個体までの距離。
- `LPb`
  - 前方 long probe による、最寄り barrier までの距離。
- `Bfd`
  - 前後方向の short probe barrier sensor。
- `Blr`
  - 左右方向の short probe barrier sensor。
- `Sg`
  - 周辺 pheromone / signal density。
- `Sfd`
  - 前後方向の signal 偏り。
- `Slr`
  - 左右方向の signal 偏り。
- `Gen`
  - 前方隣接個体との genome similarity。
  - kin recognition や同種判定のような行動を進化させられる。

この方式は、初期 sandbox の sensor を「画像」ではなく意味の明確な低次元 receptor とする設計に向いている。

### 内部状態を action から操作する

BioSim4 の action には移動以外に、自分自身の内部状態を変更するものがある。

- `OSC`
  - internal oscillator の周期を変更する。
- `LPD`
  - long probe の sensing distance を変更する。
- `Res`
  - responsiveness、すなわち action の発現しやすさを変更する。

この発想を一般化すると、

- sensor range を一時的に伸ばす
- sensor gain を変更する
- motor gain を変更する
- attention 対象を変更する
- metabolic mode を切り替える

など、「action が外界だけでなく自分自身を制御する」仕組みに拡張できる。

### 複数の movement primitive

BioSim4 では NN が直接座標を指定するのではなく、複数の移動 action が「移動したい方向への urge」を出し、それらを合成して最終移動を決める。

例:

- `MX` / `MY`
  - world X/Y 軸方向への移動成分。
- `Mfd`
  - 直前の進行方向へ前進。
- `Mrv`
  - 直前の進行方向と逆へ後退。
- `MRL`
  - 進行方向に対する左右成分。
- `Mrn`
  - random direction への移動成分。
- 方位別 action
  - east / west / north / south / left / right も実装されている。

各 action output は最終的に X/Y の movement urge に加算され、`tanh` と responsiveness を通して確率的な 1-cell movement へ変換される。

今回の連続空間版では、これを

```text
action output
    -> desired thrust / steering
    -> force composition
    -> dynamics integration
```

と一般化できる。

### Pheromone / environmental signal

- agent は `SG` action により scalar signal を周囲へ放出できる。
- signal は 2D world 上の field として蓄積され、時間とともに減衰する。
- 他個体は `Sg`, `Sfd`, `Slr` sensor でその signal を読む。
- 直接通信ではなく、環境を媒介した stigmergy を進化させられる。

将来的には、

- 複数種類の pheromone
- diffusion
- decay rate
- emission cost
- receptor sensitivity

などを遺伝形質にできる。

### Genetic similarity sensor

- `Gen` sensor は前方個体との genome similarity を返す。
- 遺伝的に近い個体と遠い個体で行動を変える回路を進化させられる。
- kin selection、群れ形成、同種認識、攻撃対象選択などの実験に応用できる。

### Random sensor

- `Rnd` は単なるノイズではなく、NN が確率的方策を作るための入力として使える。
- deterministic NN のままでも、random receptor との接続を進化させることで stochastic behavior を獲得できる。
- 明示的な stochastic policy layer を実装しなくても探索的行動が生じ得る。

### Oscillator sensor

- `Osc` は個体内 clock のような周期信号。
- action `OSC` によって oscillator period 自体を変更できる。
- memoryless feed-forward brain でも周期的な探索、左右運動、間欠的な signal emission などを生成できる。
- 初期段階で RNN を使わず時間依存行動を与えたい場合に有用。

### Kill / predation primitive

- `Kill` / `Klf` は前方隣接個体を殺す action。
- 強い action output がそのまま必ず実行されるのではなく、threshold と probability を介して発動する。
- 今回の sandbox では、これをより一般的な InteractionSystem として
  - 一定距離
  - 一定接触時間
  - attack strength
  - energy cost
  - predator/prey condition
  などへ拡張できる。

### Action responsiveness

- NN は `Res` action により自身の responsiveness を変更できる。
- responsiveness は movement、signal emission、kill など複数 action の実行確率に共通して作用する。
- これは「brain output」と「実際の行動発現」の間に調整可能な global gain を置く設計とみなせる。
- activity / energy cost と組み合わせると、省エネ状態と高反応状態の切り替えへ発展できる。

### Sensor range を行動で変更する

- `LPD` action により long-probe distance を個体自身が変更できる。
- sensing ability を固定性能にせず、状況に応じて使い分けられる。
- 今回の sandbox では sensing distance に energy cost を導入すると、
  - 通常は短距離・低コスト
  - 必要時だけ長距離・高コスト
  という adaptive sensing が進化する可能性がある。

### Population / directional-density sensor

- 単に「近くに何匹いるか」だけでなく、前後・左右どちらに密度が偏っているかを sensor として持つ。
- 個体を一体ずつ認識しなくても、
  - 群れへ近づく
  - 群れを避ける
  - 群れの端を移動する
  などの collective behavior を小さい NN で実現できる。

### 面白い点の要約

BioSim4 から特に取り込みやすい要素:

- gene を NN edge とする直接 encoding
- genome length / connection 数の進化
- sensor -> action の直接反射を許す sparse neural circuit
- random receptor
- oscillator receptor
- genetic-similarity receptor
- pheromone / environmental signal
- directional population-density sensing
- self-modifying action
  - responsiveness
  - oscillator period
  - sensor range
- predation / kill primitive
- genotype -> phenotype として出生時に brain を構築する設計

これらは大規模な deep neural network を導入せず、低次元 sensor と小規模 network のままで豊かな行動進化を観察するという点で、今回の sandbox の方向性と相性がよい。
