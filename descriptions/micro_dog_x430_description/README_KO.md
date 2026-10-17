# Micro Dog X430: 임시 몸체 + CAD 기반 URDF

이 패키지는 수정한 X430 CAD를 시각 형상으로 사용한 **초기 시뮬레이션용 로봇 설명**입니다. 중앙 몸체는 나중에 치수를 바꾸기 위한 임시 BOX입니다. 완성된 기구 설계, 모터 제어 보정, 충돌 없는 동작 범위, Isaac 학습 준비 완료를 뜻하지 않습니다.

## 포함 내용

- `urdf/micro_dog_x430.urdf`: 상대경로 STL, 일반 URDF importer용
- `urdf/micro_dog_x430_ros.urdf`: ROS `package://` 경로 버전
- `config/robot_parameters.json`: 몸체/관절 부착 위치/잠정 동역학 수정
- `config/cad_geometry.json`, `cad_frames.json`: CAD 측정값, 링크별 형상/원점, 근거
- `meshes/`: 미터 단위 STL 32개. URDF scale=1
- `scripts/generate_urdf.py`: 표준 Python만 사용하는 생성기
- `scripts/export_cad_meshes.py`: 원본을 저장/수정하지 않는 FreeCAD 재추출기
- `scripts/validate_urdf.py`: 생성된 실제 XML/STL 검증
- `scripts/render_urdf.py`: 생성된 URDF를 읽고 FK로 자세를 그리는 별도 렌더러
- `validation/neutral.png`, `bent.png`, `neutral_top.png`: URDF 기반 미리보기
- `validation/report.json`, `poses.json`: 검사/자세 수치

총 17 links, 12 revolute joints, 4 fixed foot joints입니다. 이름은 FL/FR/RL/RR이며 CAD의 LR은 여기서 RL입니다. 롤은 XM430 4개, 피치/무릎은 XL430 8개에 대응합니다.

## 바로 수정하기

패키지 폴더에서 실행합니다. 파일 경로에 공백이 있으면 따옴표로 감싸세요.

```bash
python3 scripts/generate_urdf.py
```

몸체만 220×30×25 mm, 질량 0.8 kg으로 변경:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p=Path('config/robot_parameters.json')
c=json.loads(p.read_text())
c.update(body_length=0.220, body_width=0.030, body_height=0.025, body_mass=0.8)
p.write_text(json.dumps(c,indent=2)+'\n')
PY
python3 scripts/generate_urdf.py
python3 scripts/validate_urdf.py
```

**몸체 크기를 바꾸어도 다리 부착 위치는 자동으로 이동하지 않습니다.** 박스의 크기와 실제 모터/다리 부착점은 별도 설계 변수이기 때문입니다. 앞뒤 롤 부착점을 ±110 mm, 좌우를 ±35 mm로 바꾸려면:

```bash
python3 - <<'PY'
import json
from pathlib import Path
p=Path('config/robot_parameters.json')
c=json.loads(p.read_text())
c['hip_attachments']={'FL':[.110,.035,0],'FR':[.110,-.035,0],
                      'RL':[-.110,.035,0],'RR':[-.110,-.035,0]}
p.write_text(json.dumps(c,indent=2)+'\n')
PY
python3 scripts/generate_urdf.py
python3 scripts/validate_urdf.py
python3 scripts/render_urdf.py
```

이 변경은 각 다리의 모든 하위 링크와 해당 고정 롤 모터/골반 시각 형상을 함께 옮깁니다. 몸체 관성도 부착점 변화에 따라 다시 계산합니다. 예시 치수가 기구적으로 맞는다는 뜻은 아닙니다. 새 치수의 간섭과 실제 고정 구조를 설계해야 합니다.

## 좌표와 초기 치수

단위: m, kg, rad. 로봇 +X 전방, +Y 왼쪽, +Z 위쪽. base_link 원점은 초기 네 롤 혼 중심의 중점입니다. 모든 링크 원점의 초기 방향은 base_link와 같고, 좌우 반사는 STL 정점에 적용하여 오른손 좌표계를 유지합니다.

- 임시 박스: 180×24×20 mm, 박스/탑재물 질량 0.60 kg
- 롤 혼 중심: 앞뒤 ±95 mm, 좌우 ±29 mm, 높이 0
- 피치–무릎 회전축 간 거리: 142.5 mm
- 무릎–발 고정축 거리: 145.5 mm
- 발 고정축 아래 TPU 형상: 약19.50 mm
- 초기 전체 질량: 2.28 kg = 박스/탑재물0.60 + 고정 모터/골반0.12×4 + 가동 다리0.30×4 (모두 잠정)

박스는 기존 롤 모터와 겹치지 않도록 좁게 시작합니다. 박스와 골반을 실제로 연결하는 브래킷/나사/배터리/전자부품은 설계하지 않았습니다. CAD 네 모서리 배치는 대퇴가 수평이고 종아리가 아래로 향한 저장 자세입니다. URDF의 0 rad는 이 CAD 자세이며 모터의 전기 영점이 아닙니다. 뒤쪽/앞쪽 다리의 CAD 배치가 단순 대칭이 아니므로, 임의로 대칭화하지 않았습니다.

`validation/poses.json`은 기본 CAD 자세와 예시 굽힘 자세의 발 원점과 최저 시각 형상 기준 base 높이를 제공합니다. 이 높이는 접촉/안정성 보장이 아닙니다. 입력 치수를 변경한 뒤 렌더러를 다시 실행해 갱신하세요.

## 중요한 단순화

1. 실제 크랭크–푸시로드 평행사변형 폐루프를 URDF 트리의 **등가 무릎 관절**로 바꾸었습니다. 크랭크/푸시로드/작은 캡은 움직임이 틀린 채 고정되지 않도록 시각 형상에서 제외했습니다. 무릎 q는 실제 XL430 축각이 아닙니다. 하드웨어에 보내려면 기구학 변환, 방향, 영점, 기어/링크 전달 관계를 별도로 검증해야 합니다.
2. 발은 종아리에 fixed로 연결했습니다. TPU 탄성/실제 축 유격은 모델링하지 않습니다.
3. 모터 시각 형상은 하우징과 혼이 함께 포함된 참조 CAD입니다. 혼을 독립 회전시키지 않습니다. 제조사 참조 어셈블리에 포함된 별도 나사/스페이서 객체는 시각적으로 떠 있지 않도록 제외하고, 필요한 설치 스페이서만 따로 포함했습니다. 네 모서리 overview는 출력 부품만 포함하므로 모터의 대칭 배치는 RR에서 재구성한 것이며 실제 네 방향 장착 적합성을 검증한 것은 아닙니다.
4. 질량, 질량중심, 관성, effort/velocity/각도 제한, damping 모두 **잠정값**입니다. 가동 링크는 형상 AABB의 균일 박스 관성을 사용합니다. 양의 정부호 검사는 수치적 유효성이지 실제 관성의 정확성 검증이 아닙니다. 고정 모터/골반의 질량은 롤 부착점의 작은 박스로 근사하고 base 관성에 합산합니다.
5. collision은 가동 링크별 보수적 AABB 박스와 중앙 박스입니다. 고정 골반/롤 모터 전체의 collision은 포함하지 않았습니다. 세밀한 접촉/자기충돌 모델이 아니며 관절 부근 박스가 겹칠 수 있습니다. 시뮬레이터의 인접 링크 충돌 설정과 충돌 형상 재설계가 필요합니다.
6. 미리보기는 파싱된 실제 URDF/STL의 FK 결과입니다. Isaac Sim/Isaac Lab, RViz, ROS2 런타임을 설치하거나 실행한 검증은 아닙니다. 동역학/접촉/균형/훈련 테스트는 하지 않았습니다.

## 위치 제어와 Isaac 가져오기

`urdf/micro_dog_x430.urdf`를 mesh 폴더와 함께 유지하고 importer에 전체 경로로 지정합니다. importer별 상대경로 처리 차이가 있으면 파일 위치를 기준으로 mesh path를 해석하도록 설정합니다. ROS 버전의 package URI는 ROS 패키지 경로가 필요합니다.

이 URDF 자체는 위치 제어기를 생성하지 않습니다. importer/시뮬레이터에서 12개 revolute 관절의 drive를 position 모드로 지정하고 stiffness/damping/effort/속도 제한을 실측에 맞춰 설정해야 합니다. 롤 XM430/피치 XL430/등가 무릎 XL430 그룹을 `config/actuators.json`에 표시했습니다. 임의 PID를 하드웨어에 적용하지 마세요. 고정 발 관절은 importer 설정에 따라 합쳐질 수 있으므로 importer 이후 12 자유도를 다시 확인하세요.

처음 확인할 순서: 단위/크기 → base 자세/접지 높이 → 관절별 축/부호 → 폐루프 각도 변환 → 제한/자기충돌 → 질량/관성 → 액추에이터/접촉 → 정적 안정성. 이후에 학습 환경을 구성합니다.

## ROS2 RViz

ROS2와 관련 의존성이 설치된 워크스페이스의 src에 패키지를 놓고:

```bash
colcon build --packages-select micro_dog_x430_description
source install/setup.bash
ros2 launch micro_dog_x430_description display.launch.py
```

joint_state_publisher_gui에서 자세를 움직여 확인하는 최소 launch입니다. ros2_control/하드웨어 통신은 포함하지 않습니다. 파라미터를 바꾼 경우 생성 후 다시 build하세요.

## CAD부터 재생성

FreeCAD Python API를 사용할 수 있는 Python으로 실행합니다. 저장된 원본 파일 두 개가 있어야 합니다.

```bash
/usr/bin/python3 scripts/export_cad_meshes.py --cad-dir /path/to/Micro_Dog_X430_working
python3 scripts/generate_urdf.py
python3 scripts/validate_urdf.py
python3 scripts/render_urdf.py
```

FreeCAD 모듈 위치가 다르면 `--freecad-lib /path/to/freecad/lib`를 지정합니다. STL은 0.15 mm tessellation, 미터로 변환하여 저장합니다. `cad_frames.json`은 현재 CAD에서 측정한 관절/변환 명세입니다. 기구/조립 위치를 바꾼 새 CAD에서는 이 측정값도 다시 추출/검증해야 하며 기존 값을 그대로 쓰면 안 됩니다. 일반 몸체/부착점 수정에는 FreeCAD가 필요 없습니다. 검증기는 NumPy, 렌더러는 NumPy/Pillow/C++ 컴파일러와 DejaVu 글꼴이 필요합니다.

## 출처와 라이선스

수정 기구 형상의 기반: https://github.com/moieboy9999/Micro_Dog , upstream commit `68373f962d8916d3e81a07630844f12e3dfbe927`. 해당 mechanical/docs/URDF/params의 CC BY-NC-SA 4.0 조건과 표기를 유지합니다. 이 패키지는 기존 URDF를 복사한 것이 아니라 수정 CAD에서 새로 생성했습니다. 생성/검증 도구는 GPL-3.0-or-later로 배포합니다. ROBOTIS 모터 참조 CAD는 제3자 자료이므로 위 라이선스로 재허가한다고 주장하지 않습니다. 저장소의 LICENSE/THIRD_PARTY_NOTICES 및 원 출처 조건을 함께 확인하세요.
