import fitz,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parents[1]
doc=fitz.open(OUT/'base_revision1.pdf')
font=str(OUT/'source'/'ManualNotoKR.ttf')
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
pdfmetrics.registerFont(TTFont('ManualKoreanSafe',font))
def text(page,rect,s,size=9,color=(.13,.25,.34),fill=(1,1,1)):
 page.draw_rect(fitz.Rect(rect),color=None,fill=fill,overlay=True)
 lines=[]
 for line in s.split('\n'):
  lines.extend(simpleSplit(line,'ManualKoreanSafe',size,rect[2]-rect[0]) if line else [''])
 lineheight=size*1.682
 if len(lines)*lineheight > rect[3]-rect[1]+size*.5:raise ValueError(('text overflow',page.number+1,s))
 buf=BytesIO();c=canvas.Canvas(buf,pagesize=(page.rect.width,page.rect.height));c.setFont('ManualKoreanSafe',size);c.setFillColorRGB(*color)
 y=page.rect.height-rect[1]-size*1.16
 for line in lines:
  c.drawString(rect[0],y,line);y-=lineheight
 c.save();overlay=fitz.open(stream=buf.getvalue(),filetype='pdf');page.show_pdf_page(page.rect,overlay,0)
def image(page,rect,name):
 page.draw_rect(fitz.Rect(rect),color=None,fill=(1,1,1),overlay=True)
 page.insert_image(fitz.Rect(rect),filename=str(OUT/'assets'/f'{name}.png'),keep_proportion=True,overlay=True)
map={1:['overview'],8:['cables'],9:['nuts_leg','nuts_yoke'],10:['crank_e','crank_a'],11:['distal_e','distal_a'],12:['preload'],13:['pitch_e','pitch_a'],14:['knee_e','knee_a'],15:['access_36','access_144'],16:['access_36_full','access_144_full'],17:['large_e','large_a'],18:['shank_e','shank_a'],19:['foot_e','foot_a'],20:['crank_horn_e','crank_horn_a'],21:['xm_e','xm_a'],22:['roll_e','washer_stack'],23:['carriers_e','carriers_a'],24:['support_e','support_a'],25:['jointmap'],27:['four_corner_motors']}
stage=set([10,11,13,14,17,18,19,20,21,22,23,24])
for n,names in map.items():
 p=doc[n-1];blocks=[b for b in p.get_text('dict')['blocks'] if b['type']==1]
 if n in stage:
  p.add_redact_annot(fitz.Rect(28,145,815,438),fill=(1,1,1));p.apply_redactions(images=1,graphics=0)
  image(p,(35,164,495,426),names[0]);image(p,(540,165,795,295),names[1])
  text(p,(40,148,495,164),'골반 확대 · 다리 형상 생략' if n in [23,24] else '대퇴 관절 확대 · 모터 생략' if n==17 else '분리 표시 / 실제 삽입축',8)
  text(p,(540,148,795,164),'와셔 위치 확대 / 네 곳 중 한 세트' if n==22 else '조립 후 참고',8)
 elif n==9:
  p.add_redact_annot(fitz.Rect(30,110,815,535),fill=(1,1,1));p.apply_redactions(images=1,graphics=0)
  image(p,(35,120,405,360),names[0]);image(p,(440,120,805,360),names[1])
 else:
  for block,name in zip(blocks,names):image(p,block['bbox'],name)
# Consistent reading key. All frame geometry is newly projected from the source assembly.
p=doc[1];p.add_redact_annot(fitz.Rect(520,120,810,342),fill=(1,1,1));p.apply_redactions(images=0,graphics=0);text(p,(535,130,800,330),'그림 색상\n주황: 이번 단계에 추가하는 부품\n회색: 먼저 조립한 출력물\n진회색: 모터 참고 형상\n청록: 베어링 / 와셔\n파랑: 나사와 삽입축\n황동색: 너트\n\n화살표는 실제 나사축을 따릅니다.\n체결품은 치수에 맞춘 개략 형상입니다.',9)
text(doc[0],(600,22,810,40),'ASSEMBLY MANUAL / REV 3 - FIGURES',7)
text(doc[8],(40,385,405,520),'M3 너트 6개 미리 넣기\n1 안쪽 종아리: 중간 2개 + 발끝 1개\n2 반대판 큰 관절: 1개\n3 작은 캡: 각 1개, 두 캡 합계 2개\n너트는 육각 포켓의 받침면에 맞춥니다.',9)
text(doc[8],(445,385,805,520),'요크 M2.5 너트 2개\n측면 열린 슬롯에서 넣어 두 나사축에 맞춥니다.\n나사 삽입 방향과 너트 삽입 방향은 다릅니다.\n대변 5 × 두께 2 mm. M3는 사용하지 않습니다.',9)
# Replace only right-hand figure descriptions. Bottom safety/dimension notes remain intact.
notes={
10:'1 푸시로드 + 6×10×2.5 베어링\n2 작은 캡 + 미리 넣은 M3 너트\n파란 M3×12: 크랭크 뒤에서 캡 방향.\n와셔 없음. 오른쪽은 결합 후 전체 모습.',
11:'1 종아리 반대판\n2 작은 캡 + 미리 넣은 M3 너트\n파란 M3×14: 반대판 안쪽에서 캡 방향.\n푸시로드 전체를 잘라내지 않고 표시했습니다.',
13:'1 빈 대퇴. 피치 XL은 뒤쪽으로 분리 표시.\nM2×8 네 개를 대퇴에서 피치 혼으로.\n무릎용 M2.5×20은 앞 페이지에서 선삽입.\n아직 무릎 모터와 캐리어를 붙이지 않습니다.',
14:'1 무릎 XL / 2~5 XL 키 스페이서 네 개\n기존 대퇴는 한 개만 표시합니다.\n긴 나사는 이미 선삽입된 상태입니다.\n아래 두 나사는 다음 페이지의 임시 접근 자세에서 조입니다.',
17:'1 안쪽 종아리 / 2 큰 캡\n청록 링: MR137ZZ 7×13×4.\n대퇴와 두 반축 사이에 넣습니다.\n이 단계에는 반대판을 추가하지 않습니다.',
18:'1 반대판을 가져와 큰 캡과 맞춥니다.\nM3×22 한 개 + 중간 M3×18 두 개.\n크랭크는 최종 위치에 맞춰 표시했지만\n혼 나사 네 개는 08단계에서 체결합니다.',
19:'1 TPU 발을 발끝 형상 사이에 넣습니다.\nM3×18 한 개, 반대판에서 안쪽 너트로.\n발을 넣는 방향은 형상을 따라 맞추고\nPLA 판을 나사 힘으로 휘어 맞추지 않습니다.',
20:'1 크랭크를 무릎 XL 혼에 맞춥니다.\n파란 M2×8 네 개를 크랭크에서 혼으로.\n이미 연결한 종아리와 푸시로드도 표시.\n중앙 혼 고정나사는 기존 것을 유지합니다.',
21:'1 요크 / 2~5 XM 케이스 스페이서\n스페이서와 요크를 축 방향으로 분리 표시.\nM2.5×14 네 개로 기존 코너 나사를 교체.\n출력 혼은 모터에서 분해하지 않습니다.',
22:'1 빈 혼 쪽 롤 캐리어\n나사머리 → 0.3 mm 와셔 → 캐리어 → 혼.\nM2×6 네 개 + 와셔 네 개.\n피치 모터를 넣기 전에 네 나사를 마칩니다.',
23:'1 반대쪽 베어링 캐리어\n완성한 다리와 피치 모터를 함께 표시.\nM2.6×8 지정 태핑, 위 4개 + 아래 4개.\n회색 캐리어도 이미 혼에 연결된 상태입니다.',
24:'1 고정 지지대 / 2 MR137ZZ 베어링\n지지축을 베어링에 맞춰 넣고 요크를 닫습니다.\nM2.5×8 두 개, 미리 넣은 너트 두 개.\n중앙 몸체는 이 설명서에 포함하지 않습니다.'}
for n,s in notes.items():text(doc[n-1],(525,309,810,430),s,9)
text(doc[14],(45,367,400,391),'피치 주변 확대 · 대퇴 끝부분은 프레임 밖',8)
text(doc[14],(442,367,800,391),'피치 주변 확대 · 전체 위치는 다음 페이지',8)
# Keep captions consistent with revised scene colors and actual stage additions.
text(doc[15],(35,76,810,100),'주황은 회전한 피치 케이스, 청록은 공구축입니다. 고정 혼과 대퇴는 회전시키지 않았습니다.',10)
text(doc[14],(47,468,402,489),'청록: 지름 3 mm 공구축. 십자 날 호수 아님.',9,fill=(.945,.961,.969))
text(doc[16],(45,125,810,143),'아직 나사 없음 · 큰 캡을 받친 뒤 다음 단계에서 M3×22로 체결',10,color=(.7,.34,.1),fill=(.945,.961,.969))
text(doc[17],(45,125,810,143),'M3×22 원통머리 ×1 + M3×18 원통머리 ×2 / 미리 넣은 M3 너트 사용',10,color=(.7,.34,.1),fill=(.945,.961,.969))
text(doc[16],(45,470,490,531),'큰 캡은 받쳐 둡니다. 다음 단계에서 반대판을 맞춘 뒤 큰 관절 나사를 체결합니다. 베어링 외륜을 나사 힘으로 억지로 끌어당기지 마세요.',10)
text(doc[16],(535,470,800,531),'청록 베어링을 대퇴에 넣고 양쪽 Ø7 반축을 맞춥니다. 나사 방향과 길이는 다음 페이지에서 확인합니다.',10)
# Explicit small-bearing fit boundary, discovered from exact source geometry.
text(doc[6],(38,520,805,551),'작은 베어링 주의: 그림은 반축 이음면에 중심을 맞춘 명목 위치입니다. 내륜 모서리와 출력 반축 뿌리 필렛의 실제 끼움은 시험 조립으로 확인하세요.',8,color=(.65,.29,.08))
text(doc[26],(540,330,805,445),'모터 방향 확인\n진회색: 롤 / 무릎 모터\n주황: 피치 케이스와 캐리어\n\n모터는 RR 원본 형상을 각 코너의 최종 배치에 변환한 참고도입니다. 네 방향의 실제 장착 적합성·몸체 간섭은 미검증입니다.',9)
# Replace complete obsolete color paragraphs, rather than partial overlays.
for page,rect,content in [
 (doc[0],(488,240,810,366),'이 설명서의 기준\n최종 CAD 형상을 기준으로 그림을 다시 만들었습니다. 주황은 추가 부품, 파랑은 나사, 황동색은 너트, 청록은 베어링·와셔입니다. 분리 그림은 삽입축을 유지하며 위치만 벌린 설명도입니다.'),
 (doc[26],(530,125,810,323),'출력 부품 조합\nRR: RR 대퇴·종아리·반대판 + RR 요크\nFR: RR 대퇴·종아리·반대판 + LR 요크\nLR: LH 대퇴·종아리·반대판 + LR 요크\nFL: LH 대퇴·종아리·반대판 + RR 요크'),
 (doc[26],(530,328,810,522),'모터 방향 확인\n진회색: 롤 / 무릎 모터\n주황: 피치 케이스와 캐리어\n\n모터는 RR 원본 형상을 각 코너의 최종 배치에 변환한 참고도입니다. 네 방향의 실제 장착 적합성·몸체 간섭은 미검증입니다.'),
 (doc[30],(38,378,810,435),'모터·혼·스페이서 참고 형상은 ROBOTIS의 저작물입니다. 원본 모터 CAD에 떠 있는 참고 나사를 구매 목록으로 세지 마세요. 본문의 파란색 체결품 표시와 지정 규격을 따릅니다.')]:
 page.add_redact_annot(fitz.Rect(rect),fill=(1,1,1));page.apply_redactions(images=0,graphics=0);text(page,rect,content,10)
for rect,title,body,bg in [
 ((34,440,505,548),'닫기 전 확인','큰 캡은 받쳐 둡니다. 다음 단계에서 반대판을 맞춘 뒤 큰 관절 나사를 체결합니다. 베어링 외륜을 나사 힘으로 억지로 끌어당기지 마세요.',(.99,.95,.90)),
 ((520,440,810,548),'삽입 방향 / 스택','청록 베어링을 대퇴에 넣고 양쪽 Ø7 반축을 맞춥니다. 나사 방향과 길이는 다음 페이지에서 확인합니다.',(.945,.961,.969))]:
 page=doc[16];page.add_redact_annot(fitz.Rect(rect),fill=bg);page.apply_redactions(images=0,graphics=0)
 text(page,(rect[0]+12,rect[1]+10,rect[2]-12,rect[1]+34),title,12,fill=bg)
 text(page,(rect[0]+12,rect[1]+38,rect[2]-12,rect[3]-10),body,10,fill=bg)
# Rebuild remaining colored information cards with matching full backgrounds.
for page,rect,title,body in [
 (doc[0],(488,240,810,366),'이 설명서의 기준','최종 CAD 형상을 기준으로 그림을 다시 만들었습니다. 주황은 추가 부품, 파랑은 나사, 황동색은 너트, 청록은 베어링·와셔입니다. 분리 그림은 삽입축을 유지하며 위치만 벌린 설명도입니다.'),
 (doc[14],(34,400,411,496),'임시 자세 A','저장 자세 대비 피치 케이스 +36.027°.\nL +X 축 오른손 회전, 중심 (0, 0, -85.5).\n청록: 지름 3 mm 공구축. 십자 날 호수 아님.'),
 (doc[26],(530,125,810,323),'출력 부품 조합','RR: RR 대퇴·종아리·반대판 + RR 요크\nFR: RR 대퇴·종아리·반대판 + LR 요크\nLR: LH 대퇴·종아리·반대판 + LR 요크\nFL: LH 대퇴·종아리·반대판 + RR 요크'),
 (doc[26],(530,328,810,522),'모터 방향 확인','진회색: 롤 / 무릎 모터\n주황: 피치 케이스와 캐리어\n\n모터는 RR 원본 형상을 각 코너의 최종 배치에 변환한 참고도입니다. 네 방향의 실제 장착 적합성·몸체 간섭은 미검증입니다.')]:
 bg=(.945,.961,.969);page.add_redact_annot(fitz.Rect(rect),fill=bg);page.apply_redactions(images=0,graphics=0)
 text(page,(rect[0]+12,rect[1]+10,rect[2]-12,rect[1]+34),title,12,fill=bg)
 text(page,(rect[0]+12,rect[1]+38,rect[2]-12,rect[3]-7),body,9.5,fill=bg)
# Source and publication audit notes, no claim of physical validation.
text(doc[30],(38,480,805,542),'REV 3: 최종 CAD 형상에서 조립 그림 재생성. 모터 참고 모델의 떠 있는 기본 나사·중복 형상을 제외했습니다. 나사 36개 축은 CAD 구멍과 대조했습니다. 베어링·체결품은 명목 치수의 설명용 형상이며 실물 공차·체결 토크·배선 동작은 미검증입니다.',8)
doc.set_metadata({**doc.metadata,'title':'Micro_Dog X430 - 한국어 조립 설명서 REV 3','subject':'CAD-based assembly figures, revised and reviewed'})
out=OUT/'Micro_Dog_X430_Assembly_Manual_KO_v3.pdf';doc.save(out,garbage=4,deflate=True);print(out)

