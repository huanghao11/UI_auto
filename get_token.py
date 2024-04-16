# import json
#
# import requests
#
#
# def get_token():
#
#     api_key = "smuwQTme7454K0x1FHF4n0Tn"
#     secret_key = "PDzTu2aey1va0V0AQY0GyWOLSIcZ5PzO"
#     token_url = "https://aip.baidubce.com/oauth/2.0/token"
#     url = f"{token_url}?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
#
#     payload = json.dumps("")
#     headers = {
#         "Content-Type": "application",
#         "Accept": "application/json"
#     }
#
#     response = requests.request("POST",url,headers=headers,data=payload)
#
#     print(response.text)
#
#     return response
#
# get_token()
def max_n(digits, n):
    digits.sort()
    num_str = str(n)
    less = False
    result = 0

    for i in range(len(num_str)):
        num = int(num_str[i])
        if less:
            result = result * 10 + digits[-1]
            continue

        next_digit = int(num_str[i + 1]) if i < len(num_str) - 1 else digits[0]
        r = binary_search(digits, num, next_digit)

        if r < num:
            result = result * 10 + r
            less = True
        elif r == num:
            result = result * 10 + r
        else:
            return -1

    return result


def binary_search(digits, target, next_digit):
    if next_digit < digits[0]:
        target -= 1

    b, e = 0, len(digits) - 1

    while b <= e:
        m = (b + e) // 2

        if e - b <= 1:
            if digits[e] <= target:
                return digits[e]
            if digits[b] <= target:
                return digits[b]
            return digits[b]
        elif digits[m] == target:
            return target
        elif digits[m] > target:
            e = m - 1
        else:
            b = m

    return digits[b]


# 测试示例
print(max_n([1, 2, 4, 9], 2533))
print(max_n([4, 2, 9, 8], 988822))
print(max_n([9, 8], 8))
print(max_n([9, 6, 3, 5], 56449))
print(max_n([1, 2, 3, 4, 5, 6, 7, 8], 8363065))
