import subprocess
import time

# 실행할 스크립트 파일 이름
etherscan_script = "etherscan.js"
visualizer_script = "visualizer.py"

# 경과 시간을 저장할 리스트
elapsed_times = []

# 5회 실행
for i in range(5):
    # etherscan.js 실행
    start_time = time.perf_counter()  # 시작 시간 기록
    subprocess.run(["node", etherscan_script])  # Node.js로 etherscan.js 실행
    end_time = time.perf_counter()  # 종료 시간 기록
    print(f"Execution time for {etherscan_script}: {end_time - start_time:.6f} seconds")

    # visualizer.py 실행
    start_time = time.perf_counter()  # 시작 시간 기록
    subprocess.run(["python", visualizer_script])  # visualizer.py 실행
    end_time = time.perf_counter()  # 종료 시간 기록
    elapsed_time = end_time - start_time  # 경과 시간 계산

    # 리스트에 경과 시간 추가
    elapsed_times.append(elapsed_time)
    print(f"Execution time for {visualizer_script}: {elapsed_time:.6f} seconds")

# 전체 실행 시간을 리스트로 출력
print("Elapsed times for visualizer.py executions:", elapsed_times)
