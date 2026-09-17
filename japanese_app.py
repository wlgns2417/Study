# -*- coding: utf-8 -*-
import html
import random
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Speak Japanese", page_icon="🇯🇵", layout="wide")

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.1rem;padding-bottom:2rem}
.jp-hero{padding:22px 25px;border:1px solid rgba(130,130,130,.24);border-radius:22px;margin:8px 0 20px 0;background:linear-gradient(135deg,rgba(80,90,180,.13),rgba(180,80,140,.08))}
.jp-hero h1{margin:0;font-size:34px}.jp-hero p{margin:7px 0 0;opacity:.72}
.jp-card{border:1px solid rgba(130,130,130,.25);border-radius:18px;padding:17px 18px;min-height:235px;margin-bottom:12px;background:rgba(120,120,120,.035)}
.jp-card .no{font-size:11px;font-weight:800;opacity:.45;letter-spacing:.08em}
.jp-card .jp{font-size:24px;font-weight:900;margin-top:7px;line-height:1.35}
.jp-card .read{font-size:14px;color:#a9a9ff;margin-top:5px;font-weight:700}
.jp-card .ko{font-size:15px;color:#62c8ff;margin-top:10px;font-weight:800;line-height:1.45}
.jp-card .ex{font-size:13px;margin-top:15px;line-height:1.6;opacity:.86;border-top:1px solid rgba(130,130,130,.15);padding-top:11px}
.jp-card .exko{font-size:12px;margin-top:5px;opacity:.62}
.badge{display:inline-block;padding:3px 8px;border-radius:999px;background:rgba(120,120,120,.13);font-size:10px;margin-right:5px;margin-top:8px;opacity:.8}
.stat{border:1px solid rgba(130,130,130,.22);border-radius:16px;padding:13px 15px;text-align:center;background:rgba(120,120,120,.03)}
.stat .n{font-size:25px;font-weight:900}.stat .t{font-size:11px;opacity:.62;margin-top:2px}
div[data-baseweb="tab-list"]{gap:8px}button[data-baseweb="tab"]{font-size:15px;font-weight:800}
</style>
""", unsafe_allow_html=True)

WORDS = [
("私","わたし","나, 저","私は韓国から来ました。","저는 한국에서 왔습니다.","기본","N5"),
("今日","きょう","오늘","今日はいい天気ですね。","오늘은 날씨가 좋네요.","시간","N5"),
("明日","あした","내일","明日は休みです。","내일은 쉽니다.","시간","N5"),
("昨日","きのう","어제","昨日は忙しかったです。","어제는 바빴습니다.","시간","N5"),
("今","いま","지금","今、何時ですか。","지금 몇 시예요?","시간","N5"),
("時間","じかん","시간","時間がありますか。","시간 있으세요?","시간","N5"),
("友達","ともだち","친구","友達と旅行します。","친구와 여행합니다.","사람","N5"),
("家族","かぞく","가족","家族は韓国にいます。","가족은 한국에 있습니다.","사람","N5"),
("会社","かいしゃ","회사","会社に行きます。","회사에 갑니다.","생활","N5"),
("仕事","しごと","일, 업무","仕事が終わりました。","일이 끝났습니다.","생활","N5"),
("休み","やすみ","휴일, 휴식","明日は休みです。","내일은 쉽니다.","생활","N5"),
("駅","えき","역","駅はどこですか。","역은 어디예요?","여행","N5"),
("空港","くうこう","공항","空港までお願いします。","공항까지 부탁합니다.","여행","N5"),
("電車","でんしゃ","전철","電車で行きます。","전철로 갑니다.","여행","N5"),
("バス","ばす","버스","このバスは空港に行きますか。","이 버스는 공항에 가나요?","여행","N5"),
("ホテル","ほてる","호텔","ホテルを予約しました。","호텔을 예약했습니다.","여행","N5"),
("予約","よやく","예약","予約しています。","예약했습니다.","여행","N5"),
("店","みせ","가게","この店は何時までですか。","이 가게는 몇 시까지예요?","쇼핑","N5"),
("入口","いりぐち","입구","入口はあちらです。","입구는 저쪽입니다.","여행","N5"),
("出口","でぐち","출구","出口はどこですか。","출구는 어디예요?","여행","N5"),
("食べ物","たべもの","음식","日本の食べ物が好きです。","일본 음식을 좋아합니다.","음식","N5"),
("水","みず","물","水をください。","물 주세요.","음식","N5"),
("お茶","おちゃ","차","お茶をお願いします。","차 부탁합니다.","음식","N5"),
("ご飯","ごはん","밥, 식사","ご飯を食べましょう。","밥 먹어요.","음식","N5"),
("肉","にく","고기","肉が好きです。","고기를 좋아합니다.","음식","N5"),
("魚","さかな","생선","この魚はおいしいです。","이 생선은 맛있습니다.","음식","N5"),
("酒","さけ","술","お酒を飲みますか。","술 드세요?","음식","N5"),
("値段","ねだん","가격","値段を教えてください。","가격을 알려 주세요.","쇼핑","N5"),
("お金","おかね","돈","お金を払います。","돈을 냅니다.","쇼핑","N5"),
("カード","かーど","카드","カードは使えますか。","카드 사용할 수 있나요?","쇼핑","N5"),
("現金","げんきん","현금","現金で払います。","현금으로 계산할게요.","쇼핑","N5"),
("大きい","おおきい","크다","もっと大きいサイズはありますか。","더 큰 사이즈 있나요?","기본","N5"),
("小さい","ちいさい","작다","少し小さいです。","조금 작습니다.","기본","N5"),
("高い","たかい","비싸다, 높다","ちょっと高いですね。","조금 비싸네요.","쇼핑","N5"),
("安い","やすい","싸다","思ったより安いです。","생각보다 쌉니다.","쇼핑","N5"),
("新しい","あたらしい","새롭다","新しい店です。","새 가게입니다.","기본","N5"),
("古い","ふるい","오래되다, 낡다","この建物は古いです。","이 건물은 오래됐습니다.","기본","N5"),
("美味しい","おいしい","맛있다","本当に美味しいです。","정말 맛있습니다.","음식","N5"),
("辛い","からい","맵다","これは辛いですか。","이거 매워요?","음식","N5"),
("甘い","あまい","달다","このケーキは甘いです。","이 케이크는 달아요.","음식","N5"),
("行く","いく","가다","明日、東京に行きます。","내일 도쿄에 갑니다.","동사","N5"),
("来る","くる","오다","友達が来ます。","친구가 옵니다.","동사","N5"),
("帰る","かえる","돌아가다","ホテルに帰ります。","호텔로 돌아갑니다.","동사","N5"),
("食べる","たべる","먹다","ラーメンを食べたいです。","라멘을 먹고 싶습니다.","동사","N5"),
("飲む","のむ","마시다","コーヒーを飲みます。","커피를 마십니다.","동사","N5"),
("見る","みる","보다","映画を見ました。","영화를 봤습니다.","동사","N5"),
("買う","かう","사다","お土産を買います。","기념품을 삽니다.","동사","N5"),
("使う","つかう","사용하다","これを使ってもいいですか。","이걸 사용해도 될까요?","동사","N5"),
("分かる","わかる","알다, 이해하다","少し分かります。","조금 압니다.","동사","N5"),
("待つ","まつ","기다리다","ここで待ってください。","여기서 기다려 주세요.","동사","N5"),
("近い","ちかい","가깝다","駅はここから近いです。","역은 여기서 가깝습니다.","여행","N5"),
("遠い","とおい","멀다","空港は遠いですか。","공항은 먼가요?","여행","N5"),
("右","みぎ","오른쪽","右に曲がってください。","오른쪽으로 돌아 주세요.","여행","N5"),
("左","ひだり","왼쪽","次の角を左です。","다음 모퉁이에서 왼쪽입니다.","여행","N5"),
("まっすぐ","まっすぐ","곧장, 똑바로","まっすぐ行ってください。","곧장 가 주세요.","여행","N5"),
("好き","すき","좋아함, 좋아하다","日本料理が好きです。","일본 요리를 좋아합니다.","감정","N5"),
("大丈夫","だいじょうぶ","괜찮음, 괜찮다","はい、大丈夫です。","네, 괜찮습니다.","회화","N5"),
("本当","ほんとう","정말, 사실","本当ですか。","정말이에요?","회화","N5"),
("一緒","いっしょ","함께","一緒に行きましょう。","같이 가요.","회화","N5"),
("写真","しゃしん","사진","写真を撮ってもいいですか。","사진 찍어도 될까요?","여행","N5"),
]

PHRASES = [
("こんにちは","こんにちは","안녕하세요","こんにちは。今日は暑いですね。","안녕하세요. 오늘은 덥네요.","인사","N5"),
("ありがとうございます","ありがとうございます","감사합니다","本当にありがとうございます。","정말 감사합니다.","인사","N5"),
("すみません","すみません","실례합니다 / 죄송합니다 / 저기요","すみません、駅はどこですか。","실례합니다, 역은 어디예요?","기본","N5"),
("お願いします","おねがいします","부탁합니다","これをお願いします。","이걸로 부탁합니다.","기본","N5"),
("大丈夫です","だいじょうぶです","괜찮습니다","袋は大丈夫です。","봉투는 괜찮습니다.","기본","N5"),
("分かりません","わかりません","모르겠습니다","すみません、分かりません。","죄송하지만 모르겠습니다.","기본","N5"),
("もう一度お願いします","もういちど おねがいします","한 번 더 부탁합니다","すみません、もう一度お願いします。","죄송하지만 한 번 더 말씀해 주세요.","기본","N5"),
("ゆっくり話してください","ゆっくり はなして ください","천천히 말해 주세요","もう少しゆっくり話してください。","조금 더 천천히 말해 주세요.","기본","N5"),
("日本語は少しだけ話せます","にほんごは すこしだけ はなせます","일본어는 조금만 할 수 있어요","日本語は少しだけ話せます。","일본어는 조금만 할 수 있습니다.","기본","N5"),
("韓国から来ました","かんこくから きました","한국에서 왔습니다","私は韓国から来ました。","저는 한국에서 왔습니다.","기본","N5"),
("これは何ですか","これは なんですか","이것은 무엇인가요?","すみません、これは何ですか。","저기요, 이건 뭐예요?","기본","N5"),
("どういう意味ですか","どういう いみですか","무슨 뜻인가요?","これはどういう意味ですか。","이건 무슨 뜻인가요?","기본","N5"),
("いくらですか","いくらですか","얼마예요?","これはいくらですか。","이건 얼마예요?","쇼핑","N5"),
("これをください","これを ください","이거 주세요","すみません、これをください。","저기요, 이거 주세요.","쇼핑","N5"),
("これにします","これに します","이걸로 할게요","じゃあ、これにします。","그럼 이걸로 할게요.","쇼핑","N5"),
("カードは使えますか","かーどは つかえますか","카드 사용할 수 있나요?","ここでカードは使えますか。","여기서 카드 사용할 수 있나요?","쇼핑","N5"),
("現金で払います","げんきんで はらいます","현금으로 계산할게요","現金で払います。","현금으로 계산하겠습니다.","쇼핑","N5"),
("袋をください","ふくろを ください","봉투 주세요","袋を一つください。","봉투 하나 주세요.","쇼핑","N5"),
("試着してもいいですか","しちゃくしても いいですか","입어봐도 될까요?","これ、試着してもいいですか。","이거 입어봐도 될까요?","쇼핑","N5"),
("別のサイズはありますか","べつの さいずは ありますか","다른 사이즈 있나요?","もう少し大きいサイズはありますか。","조금 더 큰 사이즈가 있나요?","쇼핑","N5"),
("おすすめは何ですか","おすすめは なんですか","추천 메뉴가 뭐예요?","ここのおすすめは何ですか。","여기 추천 메뉴가 뭐예요?","음식","N5"),
("これを一つください","これを ひとつ ください","이거 하나 주세요","これを一つください。","이거 하나 주세요.","음식","N5"),
("二人です","ふたりです","두 명입니다","予約していません。二人です。","예약은 안 했고 두 명입니다.","음식","N5"),
("予約しています","よやくして います","예약했습니다","七時に予約しています。","7시에 예약했습니다.","음식","N5"),
("辛くないものはありますか","からくない ものは ありますか","맵지 않은 음식 있나요?","辛くないものはありますか。","맵지 않은 음식이 있나요?","음식","N5"),
("水をください","みずを ください","물 주세요","すみません、水をください。","저기요, 물 주세요.","음식","N5"),
("お会計お願いします","おかいけい おねがいします","계산 부탁합니다","すみません、お会計お願いします。","저기요, 계산 부탁합니다.","음식","N5"),
("とても美味しいです","とても おいしいです","정말 맛있어요","これ、とても美味しいです。","이거 정말 맛있어요.","음식","N5"),
("いただきます","いただきます","잘 먹겠습니다","では、いただきます。","그럼 잘 먹겠습니다.","음식","N5"),
("ごちそうさまでした","ごちそうさまでした","잘 먹었습니다","美味しかったです。ごちそうさまでした。","맛있었습니다. 잘 먹었습니다.","음식","N5"),
("トイレはどこですか","といれは どこですか","화장실은 어디예요?","すみません、トイレはどこですか。","실례합니다, 화장실은 어디예요?","여행","N5"),
("駅はどこですか","えきは どこですか","역은 어디예요?","一番近い駅はどこですか。","가장 가까운 역은 어디예요?","여행","N5"),
("ここに行きたいです","ここに いきたいです","여기에 가고 싶어요","この地図の場所に行きたいです。","이 지도에 있는 곳으로 가고 싶어요.","여행","N5"),
("どうやって行きますか","どうやって いきますか","어떻게 가나요?","空港までどうやって行きますか。","공항까지 어떻게 가나요?","여행","N5"),
("ここから近いですか","ここから ちかいですか","여기서 가까워요?","駅はここから近いですか。","역은 여기서 가까워요?","여행","N5"),
("何分ぐらいかかりますか","なんぷんぐらい かかりますか","몇 분 정도 걸리나요?","歩いて何分ぐらいかかりますか。","걸어서 몇 분 정도 걸리나요?","여행","N5"),
("この電車で合っていますか","この でんしゃで あっていますか","이 전철이 맞나요?","新宿へはこの電車で合っていますか。","신주쿠에는 이 전철 타는 게 맞나요?","여행","N5"),
("次はどこですか","つぎは どこですか","다음은 어디예요?","次はどこの駅ですか。","다음은 어느 역이에요?","여행","N5"),
("ここで降ります","ここで おります","여기서 내릴게요","次の駅で降ります。","다음 역에서 내릴게요.","여행","N5"),
("空港までお願いします","くうこうまで おねがいします","공항까지 부탁합니다","空港までお願いします。","공항까지 부탁합니다.","택시","N5"),
("この住所までお願いします","この じゅうしょまで おねがいします","이 주소까지 부탁합니다","この住所までお願いします。","이 주소까지 부탁합니다.","택시","N5"),
("ここで止めてください","ここで とめて ください","여기서 세워 주세요","ここで止めてください。","여기서 세워 주세요.","택시","N5"),
("チェックインお願いします","ちぇっくいん おねがいします","체크인 부탁합니다","チェックインお願いします。","체크인 부탁합니다.","호텔","N5"),
("荷物を預けてもいいですか","にもつを あずけても いいですか","짐을 맡겨도 될까요?","チェックイン前に荷物を預けてもいいですか。","체크인 전에 짐을 맡겨도 될까요?","호텔","N5"),
("Wi-Fiはありますか","わいふぁいは ありますか","와이파이 있나요?","部屋にWi-Fiはありますか。","방에 와이파이 있나요?","호텔","N5"),
("何時までですか","なんじまで ですか","몇 시까지예요?","朝食は何時までですか。","아침 식사는 몇 시까지예요?","호텔","N5"),
("写真を撮ってもらえますか","しゃしんを とって もらえますか","사진 찍어 주실 수 있나요?","すみません、写真を撮ってもらえますか。","죄송한데 사진 찍어 주실 수 있나요?","여행","N5"),
("写真を撮ってもいいですか","しゃしんを とっても いいですか","사진 찍어도 될까요?","ここで写真を撮ってもいいですか。","여기서 사진 찍어도 될까요?","여행","N5"),
("ちょっと待ってください","ちょっと まって ください","잠깐 기다려 주세요","ちょっと待ってください。すぐ行きます。","잠깐 기다려 주세요. 바로 갈게요.","기본","N5"),
("今行きます","いま いきます","지금 갈게요","はい、今行きます。","네, 지금 갈게요.","회화","N5"),
("本当ですか","ほんとうですか","정말이에요?","えっ、本当ですか。","어, 정말이에요?","회화","N5"),
("いいですね","いいですね","좋네요","その店、いいですね。","그 가게 좋네요.","회화","N5"),
("そうですね","そうですね","그러네요 / 그렇군요","そうですね。私もそう思います。","그러네요. 저도 그렇게 생각해요.","회화","N5"),
("そうなんですね","そうなんですね","아, 그렇군요","あ、そうなんですね。","아, 그렇군요.","회화","N5"),
("もちろんです","もちろんです","물론이죠","もちろんです。大丈夫です。","물론이죠. 괜찮습니다.","회화","N5"),
("ちょっと難しいです","ちょっと むずかしいです","조금 어렵습니다 / 곤란합니다","今日はちょっと難しいです。","오늘은 조금 어렵습니다.","회화","N5"),
("また今度","また こんど","다음에 또 / 다음 기회에","じゃあ、また今度。","그럼 다음에 또 봐요.","회화","N5"),
("楽しみです","たのしみです","기대돼요","旅行が楽しみです。","여행이 기대돼요.","회화","N5"),
("気をつけて","きを つけて","조심해 / 잘 다녀와","気をつけて帰ってください。","조심해서 돌아가세요.","회화","N5"),
("また会いましょう","また あいましょう","또 만나요","また日本で会いましょう。","또 일본에서 만나요.","인사","N5"),
]

WCOLS = ["jp","reading","ko","example","example_ko","category","level"]
words_df = pd.DataFrame(WORDS, columns=WCOLS)
phrases_df = pd.DataFrame(PHRASES, columns=WCOLS)

if "jp_done" not in st.session_state:
    st.session_state.jp_done = set()
if "jp_favorites" not in st.session_state:
    st.session_state.jp_favorites = set()


def card(row, idx, kind, hide_ko=False, hide_reading=False):
    key = f"{kind}:{row['jp']}"
    reading = "••••••" if hide_reading else html.escape(str(row['reading']))
    meaning = "뜻을 가렸습니다" if hide_ko else html.escape(str(row['ko']))
    exko = "해석을 가렸습니다" if hide_ko else html.escape(str(row['example_ko']))
    st.markdown(f"""
    <div class="jp-card">
      <div class="no">{kind.upper()} · {idx:02d}</div>
      <div class="jp">{html.escape(str(row['jp']))}</div>
      <div class="read">{reading}</div>
      <div class="ko">{meaning}</div>
      <div class="badge">{html.escape(str(row['category']))}</div><div class="badge">{html.escape(str(row['level']))}</div>
      <div class="ex">💬 {html.escape(str(row['example']))}</div>
      <div class="exko">{exko}</div>
    </div>
    """, unsafe_allow_html=True)
    a,b = st.columns(2)
    done = key in st.session_state.jp_done
    fav = key in st.session_state.jp_favorites
    if a.button("✅ 완료" if not done else "↩ 완료취소", key=f"done_{kind}_{idx}_{row['jp']}", use_container_width=True):
        if done: st.session_state.jp_done.discard(key)
        else: st.session_state.jp_done.add(key)
        st.rerun()
    if b.button("⭐ 저장" if not fav else "★ 저장됨", key=f"fav_{kind}_{idx}_{row['jp']}", use_container_width=True):
        if fav: st.session_state.jp_favorites.discard(key)
        else: st.session_state.jp_favorites.add(key)
        st.rerun()


def render_grid(df, kind, hide_ko=False, hide_reading=False):
    for start in range(0, len(df), 3):
        cols = st.columns(3)
        for j in range(3):
            pos = start + j
            if pos < len(df):
                with cols[j]:
                    card(df.iloc[pos], pos + 1, kind, hide_ko, hide_reading)

st.markdown("""
<div class="jp-hero">
<h1>🇯🇵 Speak Japanese</h1>
<p>여행에서 바로 쓰는 일본어부터 · 읽는 법 · 자연스러운 한국어 뜻 · 실제 예문까지 한 번에</p>
</div>
""", unsafe_allow_html=True)

s1,s2,s3,s4 = st.columns(4)
s1.markdown(f'<div class="stat"><div class="n">{len(words_df)}</div><div class="t">회화 단어</div></div>', unsafe_allow_html=True)
s2.markdown(f'<div class="stat"><div class="n">{len(phrases_df)}</div><div class="t">실전 표현</div></div>', unsafe_allow_html=True)
s3.markdown(f'<div class="stat"><div class="n">{len(st.session_state.jp_done)}</div><div class="t">암기 완료</div></div>', unsafe_allow_html=True)
s4.markdown(f'<div class="stat"><div class="n">{len(st.session_state.jp_favorites)}</div><div class="t">즐겨찾기</div></div>', unsafe_allow_html=True)

st.write("")
t1,t2,t3,t4 = st.tabs(["🔥 DAY 학습","💬 전체 회화 표현","📚 전체 회화 단어","✈️ 여행 일본어"])

with t1:
    st.subheader("오늘의 일본어")
    st.caption("하루 40개 · 회화 단어 20개 + 실전 표현 20개")
    total_days = max(1, min((len(words_df)+19)//20, (len(phrases_df)+19)//20))
    c1,c2,c3 = st.columns([1,1,2])
    day = c1.selectbox("DAY", list(range(1,total_days+1)), format_func=lambda x:f"DAY {x}")
    hide_ko = c2.toggle("한국어 뜻 가리기", value=False)
    hide_read = c3.toggle("읽는 법 가리기", value=False)
    w = words_df.iloc[(day-1)*20:day*20].reset_index(drop=True)
    p = phrases_df.iloc[(day-1)*20:day*20].reset_index(drop=True)
    done_today = sum(1 for x in list(w.jp)+list(p.jp) if (f"word:{x}" in st.session_state.jp_done or f"phrase:{x}" in st.session_state.jp_done))
    st.progress(done_today / max(1, len(w)+len(p)), text=f"DAY {day} 진행률 · {done_today}/{len(w)+len(p)}")
    st.markdown("### 📚 오늘의 단어 20")
    render_grid(w,"word",hide_ko,hide_read)
    st.markdown("### 💬 오늘의 표현 20")
    render_grid(p,"phrase",hide_ko,hide_read)

with t2:
    st.subheader("전체 회화 표현")
    c1,c2,c3 = st.columns([2,1,1])
    q = c1.text_input("표현 검색", placeholder="일본어 / 읽는 법 / 한국어 뜻 검색", key="pq")
    cats = ["전체"] + sorted(phrases_df.category.unique().tolist())
    cat = c2.selectbox("상황",cats,key="pc")
    mode = c3.selectbox("보기",["전체","⭐ 즐겨찾기","✅ 암기완료"],key="pm")
    df = phrases_df.copy()
    if q:
        mask = df[["jp","reading","ko","example","example_ko"]].astype(str).apply(lambda col: col.str.contains(q,case=False,na=False)).any(axis=1)
        df = df[mask]
    if cat != "전체": df = df[df.category == cat]
    if mode == "⭐ 즐겨찾기": df = df[df.jp.map(lambda x:f"phrase:{x}" in st.session_state.jp_favorites)]
    if mode == "✅ 암기완료": df = df[df.jp.map(lambda x:f"phrase:{x}" in st.session_state.jp_done)]
    st.caption(f"{len(df)}개 표현")
    render_grid(df.reset_index(drop=True),"phrase")

with t3:
    st.subheader("전체 회화 단어")
    c1,c2,c3 = st.columns([2,1,1])
    q = c1.text_input("단어 검색", placeholder="일본어 / 읽는 법 / 한국어 뜻 검색", key="wq")
    cats = ["전체"] + sorted(words_df.category.unique().tolist())
    cat = c2.selectbox("분류",cats,key="wc")
    mode = c3.selectbox("보기",["전체","⭐ 즐겨찾기","✅ 암기완료"],key="wm")
    df = words_df.copy()
    if q:
        mask = df[["jp","reading","ko","example","example_ko"]].astype(str).apply(lambda col: col.str.contains(q,case=False,na=False)).any(axis=1)
        df = df[mask]
    if cat != "전체": df = df[df.category == cat]
    if mode == "⭐ 즐겨찾기": df = df[df.jp.map(lambda x:f"word:{x}" in st.session_state.jp_favorites)]
    if mode == "✅ 암기완료": df = df[df.jp.map(lambda x:f"word:{x}" in st.session_state.jp_done)]
    st.caption(f"{len(df)}개 단어")
    render_grid(df.reset_index(drop=True),"word")

with t4:
    st.subheader("✈️ 일본 여행에서 바로 쓰기")
    st.caption("공항 · 교통 · 음식점 · 쇼핑 · 호텔에서 급할 때 바로 찾아보는 표현")
    travel_cats = ["여행","택시","음식","쇼핑","호텔"]
    choice = st.segmented_control("상황 선택", travel_cats, default="여행")
    df = phrases_df[phrases_df.category == choice].reset_index(drop=True)
    if len(df) == 0:
        st.info("해당 상황의 표현을 준비 중입니다.")
    else:
        render_grid(df,"phrase")

st.divider()
st.caption("Speak Japanese · 회화 우선 학습용 · 영어 앱과 독립적으로 실행됩니다.")
