import re
from collections import defaultdict

# Chuỗi đầu vào
input_string = """
x_0_5=1
x_1_2=1
x_2_6=1
x_3_4=1
x_4_1=1
x_5_3=1
x_6_8=1
x_7_16=1
x_8_9=1
x_9_12=1
x_10_7=1
x_11_10=1
x_12_14=1
x_13_11=1
x_14_15=1
x_15_13=1

y_0_1=1
y_0_2=1
y_0_3=1
y_0_4=1
y_0_5=1
y_0_11=1
y_0_13=1
y_3_6=1
y_3_8=1
y_9_9=1
y_9_12=1
y_10_7=1
y_10_10=1
y_14_14=1
y_14_15=1
"""

# Hàm xử lý chuỗi đầu vào để trích xuất các hành trình và gói hàng
def parse_input(input_string):
    # Dữ liệu hành trình và gói hàng
    journey = defaultdict(list)
    deliveries = defaultdict(list)
    
    # Tách các dòng x và y
    lines = input_string.strip().splitlines()
    
    for line in lines:
        # Phân tích các dòng bắt đầu bằng 'x' - hành trình xe tải
        if line.startswith('x'):
            match = re.match(r'x_(\d+)_(\d+)=1', line)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                journey[start].append(end)
        
        # Phân tích các dòng bắt đầu bằng 'y' - gói hàng tại điểm dừng
        elif line.startswith('y'):
            match = re.match(r'y_(\d+)_(\d+)=1', line)
            if match:
                location = int(match.group(1))
                package = int(match.group(2))
                deliveries[location].append(package)
    
    return journey, deliveries

# Chuyển dữ liệu hành trình và gói hàng vào dạng đầu ra yêu cầu
def format_output(journey, deliveries):
    main_route = []
    nested_route = []
    
    # for start_point in sorted(journey.keys()):
    #     delivery_points = deliveries[start_point] if start_point in deliveries else []
    #     sub_list = [start_point, delivery_points]
    #     main_route.append(sub_list)
        
    startp = 0
    for i in range(len(journey)):
        if isinstance(startp, list):
            startp = startp[0]
        if startp in deliveries:
            delivery_points = deliveries[startp]
            nested_route.append([[startp, delivery_points]])
        else:
            delivery_points = []
        sub_list = [startp, delivery_points]
        main_route.append(sub_list)
        startp = journey[startp]
    
    # Đầu ra cho hành trình lồng nhau dựa trên hành trình xe tải
    # for start_point, delivery_points in deliveries.items():
    #     nested_route.append([[start_point, delivery_points]])
    
    return [[main_route], nested_route]

# Gọi hàm
journey_data, deliveries_data = parse_input(input_string)
output_data = format_output(journey_data, deliveries_data)

# print(journey_data)

# Kết quả
if output_data[1][0][0][0] == 0:
    output_data[1].pop(0)

print(output_data)

