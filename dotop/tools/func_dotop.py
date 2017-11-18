# -*- coding: utf-8 -*-
import calendar
from decimal import Decimal

def _rmb_upper(value):
    """人民币大写.来自：http://topic.csdn.net/u/20091129/20/b778a93d-9f8f-4829-9297-d05b08a23f80.html传入浮点类型的值返回 unicode 字符串"""
    rmbmap = [u"零",u"壹",u"贰",u"叁",u"肆",u"伍",u"陆",u"柒",u"捌",u"玖"]
    unit = [u"分",u"角",u"元",u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"亿", u"拾",u"佰",u"仟",u"万",u"拾",u"佰",u"仟",u"兆"]
    nums = map(int,list(str('%0.2f'%value).replace('.','')))
    words = []
    zflag = 0#标记连续0次数，以删除万字，或适时插入零字
    start = len(nums)-3     
    for i in range(start, -3, -1):#使i对应实际位数，负数为角分
        if 0 != nums[start-i] or len(words) == 0:
            if zflag:
                words.append(rmbmap[0])
                zflag = 0
            words.append(rmbmap[nums[start-i]])
            words.append(unit[i+2])
        elif 0 == i or (0 == i%4 and zflag < 3):#控制‘万/元’
            words.append(unit[i+2])
            zflag = 0
        else:
            zflag += 1
    if words[-1] != unit[0]:#结尾非‘分’补整字
        words.append(u"整")
    return ''.join(words)

def float_format(value):
    """float格式化，避免精度问题"""
    return float('{:.2f}'.format(Decimal(str(value or 0.0 + 0.0))))

def last_day(datetime):
    """日期当月的最后一天"""
    return str(calendar.monthrange(int(datetime.year), int(datetime.month))[1])
