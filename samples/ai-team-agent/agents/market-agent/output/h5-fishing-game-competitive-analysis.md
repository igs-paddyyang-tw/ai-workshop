# H5 捕魚類遊戲競品分析報告

> 產出日期：2026-07-27  
> 研究員：market-agent  
> 任務來源：leader-agent

---

## 一、前三名熱門 H5 捕魚類遊戲

基於 2024-2026 年市場表現、平台覆蓋率、搜尋熱度與玩家活躍度，篩選出以下三款最具代表性的 H5 捕魚射擊遊戲：

| 排名 | 遊戲名稱 | 開發商 | 上線時間 | 選擇依據 |
|------|----------|--------|----------|----------|
| 1 | **Ocean King Jackpot** | TaDa Gaming | 2023-12 | Ocean King 系列旗艦 H5 版，最高 3,000x 倍率，多平台上架 |
| 2 | **Mega Fishing** | JILI Games | 2022 | JILI 旗艦捕魚作品，RTP 97.78%，亞洲市場佔有率最高 |
| 3 | **Golden Dragon** | KA Gaming | 2022 | Sweepstakes 領域最熱門魚機，多人即時對戰，歐美市場領先 |

### 選擇依據說明

- **Ocean King Jackpot**：Ocean King 系列從街機起步，是捕魚遊戲品類的開山鼻祖品牌，H5 版延續品牌力並進入線上市場
- **Mega Fishing**：JILI Games 為 2018 年成立的 HTML5 優先開發商，專攻亞洲市場，Mega Fishing 為其最高人氣捕魚作品
- **Golden Dragon**：KA Gaming 開發，被多家評測認定為 sweepstakes 領域最受歡迎的魚機遊戲（96% RTP，4 人多人模式）

---

## 二、逐款深入分析

### 2.1 Ocean King Jackpot（TaDa Gaming）

#### 核心玩法
- 街機風格射擊，玩家控制虛擬火炮瞄準水中生物
- 場景設定為「骷髏搖滾競技場」，含魚類、龍蝦、螃蟹、鯊魚、美人魚、骷髏、吸血鬼等目標
- 三級武器系統：基礎炮（1x）、鳳凰之力（5x 彈藥消耗）、龍之力（7x 彈藥消耗）
- 多種增強道具：超級炸彈、雷射蟹、鑽頭蟹、輪盤蟹、連鎖反應
- Boss 戰：雷龍（Thunder Dragon）、搖滾骷髏（Rock Skeleton）
- 暗漩渦（Dark Whirlpool）：能量計滿後清屏
- 漩渦魚（Vortex Fish）：吸附周圍小魚

#### 商業模式
- 虛擬代幣制（Gold Coins / Sweeps Coins）
- 每次射擊消耗代幣，擊殺目標獲得倍率回報
- 漸進式累積獎池：Mini、Major、Mega 三級 Jackpot
- 最高倍率 3,000x
- 無時間限制，玩家自行決定停止時機

#### UI/UX 特色
- 搖滾主題音效，骷髏競技場視覺風格（差異化明顯）
- 自動瞄準模式（Autoplay）
- 桌面版與手機版雙端適配
- 畫面繁忙感強，多人同屏時視覺衝擊力大
- 搖滾配樂 + 「Rock Skeleton」語音互動

#### 技術架構
- HTML5 開發，瀏覽器直接運行（無需下載）
- Canvas/WebGL 渲染（推測基於 Phaser 或自研引擎）
- 支持桌面瀏覽器 + 移動端瀏覽器 + 專屬 App
- RNG 經第三方認證

---

### 2.2 Mega Fishing（JILI Games）

#### 核心玩法
- 深海冒險主題，27 種獨特海洋生物目標
- 三個遊戲房間：新手房（低注）、進階房（中注）、高手房（高注）
- 最多 4 人同桌多人模式
- 特殊 Boss：巨型鹹水鱷魚（Giant Saltwater Crocodile）、巨型章魚（Mega Octopus）
- 特殊機制：Giant Anglerfish 放電開寶箱、金色幸運輪（Golden Lucky Wheel）
- 最高倍率 950x

#### 商業模式
- RTP 高達 97.78%（業界頂尖）
- 低至中波動度，適合長時間遊玩
- 每發子彈計費，不同目標有不同倍率報酬（2x ~ 500x）
- 多級獎金系統 + 5x 乘數機會
- 亞洲市場整合 GCash、PayMaya、UPI、PhonePe 等在地支付

#### UI/UX 特色
- 3D 精美畫面，色彩鮮豔的海底世界
- 三房間設計對應不同玩家層級，降低入門門檻
- 手機優先設計（Mobile-First），中低階 Android 裝置流暢運行
- 直覺式操作：點擊/觸控射擊
- Boss 戰演出華麗，有獨立動畫序列

#### 技術架構
- HTML5 原生開發（JILI 2018 年起全線採用 HTML5）
- 不需要平台特定版本或插件
- BMM Testlabs + GLI 雙重 RNG 認證
- 支援 Android 瀏覽器、iOS Safari、桌面瀏覽器
- 低延遲設計，適合東南亞網路環境

---

### 2.3 Golden Dragon（KA Gaming）

#### 核心玩法
- 經典魚機射擊，全螢幕為遊戲區域（無轉軸、無賠付線）
- 最多 4 位隨機玩家同螢幕即時競技
- 三房間分級：銅房（0.01-0.10）、銀房（0.10-1）、金房（1-10）
- 鎖定功能（Lock）：鎖定目標自動追擊
- 自動射擊模式（Auto Shoot）：連續開火直到停止
- 高價值 Boss：Golden Dragon（300x）、Siren（200x）
- 最高倍率 300x

#### 商業模式
- RTP 96%，中等波動度
- 每顆子彈 = 下注金額，射擊即消耗
- 虛擬代幣 + Sweeps Coins 雙幣系統
- 每日登入獎勵、VIP 階層、週獎勵
- 多平台上架：Zula、Fortune Wins、Carnival Citi、Sportzino、Yay

#### UI/UX 特色
- 色彩鮮豔的水底宮殿背景
- 技巧導向：玩家瞄準與時機影響收益
- 左側統計面板：歷史擊殺、子彈消耗、獎金記錄
- 操作簡潔：點擊/觸控射擊、鎖定、自動
- 多人同屏時較混亂（4 人滿場時畫面過於擁擠）
- 手機端僅支援橫屏，畫質略顯過時

#### 技術架構
- HTML5 開發，瀏覽器即玩
- 桌面端點擊、移動端觸控
- 中等級圖形渲染，相容性優先
- 整合進多家 Sweepstakes 平台 SDK

---

## 三、橫向比較表

| 比較維度 | Ocean King Jackpot | Mega Fishing | Golden Dragon |
|----------|-------------------|--------------|---------------|
| **開發商** | TaDa Gaming | JILI Games | KA Gaming |
| **上線時間** | 2023-12 | 2022 | 2022 |
| **最高倍率** | 3,000x | 950x | 300x |
| **RTP** | 未公開 | 97.78% | 96% |
| **波動度** | 高 | 低~中 | 中 |
| **多人模式** | ✅（競爭搶 Boss） | ✅（4人同桌） | ✅（4人同螢幕） |
| **武器系統** | 3 級 + 5 種增強 | 標準炮 + Boss 機制 | 標準炮 + 鎖定 + 自動 |
| **Boss 機制** | 搖滾骷髏、雷龍 | 巨鱷、巨章魚、琵琶魚 | Golden Dragon、Siren |
| **Jackpot** | 漸進式三級（Mini/Major/Mega） | 金色幸運輪 + 5x 乘數 | 無漸進式 Jackpot |
| **主題風格** | 搖滾 + 海底（暗色系） | 深海探險（色彩鮮豔） | 經典海底（明亮風格） |
| **付費設計** | 高波動高回報 | 高 RTP 穩定型 | 中等均衡型 |
| **目標市場** | 全球（偏歐美 Sweepstakes） | 亞洲（東南亞、印度優先） | 歐美 Sweepstakes 市場 |
| **手機適配** | ✅ 桌面 + 移動端 | ✅ Mobile-First | ✅（僅橫屏，略過時） |
| **技術底層** | HTML5 | HTML5（Mobile-First） | HTML5 |

### 優劣勢分析

| 遊戲 | 優勢 | 劣勢 |
|------|------|------|
| **Ocean King Jackpot** | 品牌力強（街機時代知名度）；3,000x 超高爆發力；主題差異化（搖滾風）；漸進式 Jackpot 刺激 | 畫面過於繁忙；RTP 未公開引發信任疑慮；高波動不適合休閒玩家 |
| **Mega Fishing** | 97.78% 頂尖 RTP；BMM+GLI 雙認證；Mobile-First 設計佳；亞洲在地支付整合完善；低門檻三房間設計 | 最高倍率 950x 相對保守；Boss 種類較少；品牌知名度不及 Ocean King |
| **Golden Dragon** | 技巧影響收益（差異化）；多平台覆蓋廣；Freeze Bomb+Crystal Win 策略深度；即時多人競技感強 | 300x 最高倍率偏低；4 人滿場時混亂；手機端畫質過時；缺乏漸進式 Jackpot |

---

## 四、市場趨勢與機會點

### 4.1 市場趨勢

1. **H5 遊戲市場高速成長**：全球 H5 遊戲市場 2024 年規模約 13.24 億美元，CAGR 預估 9.49%，捕魚射擊為其中高成長品類

2. **街機到線上的遷移加速**：Fish table game 從實體街機/Internet Café 快速轉移至線上 HTML5 平台，sweepstakes + social casino 模式為主要商業出口

3. **亞太主導地位**：亞太地區佔射擊類遊戲市場 46.9% 份額（2024），東南亞為捕魚遊戲最大消費市場

4. **Skill-based 混合機制興起**：純運氣型正轉向「技巧+運氣」混合型，玩家瞄準、時機選擇、彈藥管理成為差異化要素

5. **多人即時競技化**：從單機捕魚進化為 2-4 人即時同屏競爭，社交元素成留存關鍵

6. **漸進式 Jackpot 標配化**：大型累積獎池已成為頭部產品標配功能

### 4.2 機會點

| 機會 | 說明 | 建議方向 |
|------|------|----------|
| **亞洲在地化缺口** | Ocean King 偏歐美、Golden Dragon 偏歐美，JILI 獨佔亞洲但品牌力不足 | 針對台港澳/東南亞華人市場打造在地化 H5 捕魚，整合街口/LINE Pay 等在地支付 |
| **PvP 社交深度不足** | 現有多人模式僅「同屏射擊」，缺乏組隊、對戰排名、公會系統 | 引入組隊 Boss Raid、PvP 競技場排名賽、工會系統，強化社交留存 |
| **敘事與 IP 化空白** | 三款遊戲均缺乏劇情線和 IP 聯動 | 結合知名 IP（海王、航海王等）或原創世界觀，增加成長線與收集系統 |
| **Mobile-First + PWA** | 許多平台仍走 App 包裝，純 PWA 體驗有機會搶佔免安裝市場 | PWA + Service Worker 離線支援 + 推播通知，無需下載即玩 |
| **中等波動度市場空缺** | Ocean King 偏高波動、Mega Fishing 偏低波動，中間地帶機會 | 設計可調波動度系統（玩家自選風險偏好房間） |
| **直播 + 觀戰整合** | 捕魚遊戲具備觀賞性但缺乏觀戰/直播功能 | 整合直播 SDK + 觀戰模式，可配合實況主行銷 |

---

## 五、結論

H5 捕魚射擊遊戲市場正從街機時代的單純射擊進化為「技巧+社交+累積獎池」的複合型產品。三款頭部產品各有側重：Ocean King 靠品牌力和高爆發、Mega Fishing 靠高 RTP 和亞洲在地化、Golden Dragon 靠技巧深度和多平台覆蓋。

**最大空缺在於**：尚未出現一款同時具備「強 IP/敘事」+「深度社交 PvP」+「亞洲在地支付」+「Mobile-First PWA」的 H5 捕魚產品。這是新進者的最佳切入機會。

---

## 參考來源

- 🔗 https://www.strafe.com/esports-betting/casino/sweepstake-casino/fish-table-games/ocean-king-jackpot/
- 🔗 https://sweepskings.com/sweepstakes-casinos/games/fish-tables/golden-dragon/
- 🔗 https://megafishinggame.top/
- 🔗 https://jackpotfishing.net/
- 🔗 https://www.sweepschaser.com/fish-games/
- 🔗 https://jiligames.com/PlusIntro/74
- 🔗 https://www.fortunebusinessinsights.com/shooter-games-market-113013
- 🔗 https://www.cognitivemarketresearch.com/h5-games-market-report
- 🔗 https://bkmsracing.com/ (Ocean King Jackpot Guide)
- 🔗 https://jackpotfishingindia.com/ (JILI certification info)
