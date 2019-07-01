import re


def cut_string(s, _start, _end):
    pattern1 = re.compile(_start)
    pattern2 = re.compile(_end)

    var_list = []
    first_cut_list = re.split(pattern1, s)
    for i in first_cut_list[1:]:
        var_list.append(re.split(pattern2, i)[0])

    return var_list


def cut_string1(s):
    s1 = s.split("$")
    return [i.split(")")[0][1:] for i in s1[1:]]


if __name__ == "__main__":
    text = "您好，您的快递已经送到$(address)，快递编号$(trackingnumber)，请尽快领取。有问题请联系$(couriermobile)。"
    text2 = "【伟仕小贷】您有一个见面礼福袋还未领取，最高可得300元贴金券！登录手机app伟仕小贷点击首页右下角小猪浮标，领取福袋！如已领取请忽略，退订回复TD。	"
    text1 = "您的验证码$(otpcode)，该验证码5分钟内有效，请勿泄漏于他人！"
    res = cut_string(text, "\(", "\)")
    print(res)
    res1 = cut_string1(text)
    print(res1)
