import re
from entity_extraction.src.config.suffix import (COMPANY_SUFFIXES, 
                                              COMPANY_PREFIXES)

# following comment/logic are designed for Chinese market

# 按长度降序排列，确保正则引擎优先匹配长后缀（如 "集团股份有限公司" 优先于 "股份有限公司"）
sorted_suffixes = sorted(COMPANY_SUFFIXES, key=len, reverse=True)
sorted_prefixes = sorted(COMPANY_PREFIXES, key=len, reverse=True)

# 动态拼接正则字符串
COMPANY_SUFFIX_PATTERN = (
    r"(?:"
    + "|".join(map(re.escape, sorted_suffixes))
    + r")"
)
COMPANY_PREFIX_PATTERN = (
    r"^(?:"
    + "|".join(map(re.escape, sorted_prefixes))
    + r")[:：]?"
)

# 直接基于列表生成纯后缀集合，用于二次清洗拦截
PURE_SUFFIX_SET = set(COMPANY_SUFFIXES)


#用于处理（东阿县）酿造有限责任公司 &（北京）智能制造有限公司的括号行政区
_OPTIONAL_REGION_RE = r"(?:[\(（][^\)）]+[\)）])?"

# 括号行政区后可跟少量行业描述，如：
# （东阿县）酿造有限责任公司 &（北京）智能制造有限公司 此处字符限制0-8
_OPTIONAL_INDUSTRY_RE = r"[\u4e00-\u9fff]{0,8}"

# 找到最长符合的pattern
COMPANY_NAME_RE = re.compile(
    r"(?:[A-Z]{2,}\s*)?[\u4e00-\u9fff]{2,}" + _OPTIONAL_REGION_RE + _OPTIONAL_INDUSTRY_RE + COMPANY_SUFFIX_PATTERN
)

_LEADING_NOISE_RE = re.compile(r"^[，。、“”‘’：:；;（）()\[\]【】《》\s与和及]+")

# 把一段文本拆成多个候选公司（split），而不是做语义清洗
# 注意：不要添加 "公司" 等公司主体词，否则会破坏合法公司名称。
_COMPANY_CONNECTOR_RE = re.compile(r"(?:的|与|和|及|、|;|；|旗下|子公司|股东|由|任|来到|关于|近日|在)")

# 只能从字符串第一个字符开始匹配
# 国内人形机器人头部企业智元创新（上海）科技股份有限公司 -> 不可以
# 头部企业智元创新（上海）科技股份有限公司 -> 可以
_FIELD_PREFIX_RE = re.compile(COMPANY_PREFIX_PATTERN)

_RELATION_WORDS = ("保荐机构", "经营单位", "采购单位", "供应商", "申请单位", "企业")


class ChineseCompanyExtractor:
    def extract(self, text: str) -> list[str]:
        '''
        purpose: 对整段文本做正则匹配，找出所有疑似公司名片段，
                再逐个调用 _split_companies 做进一步切分
        '''
        if not text:
            return []

        candidates: list[str] = []
        for match in COMPANY_NAME_RE.finditer(text):
            candidate = _LEADING_NOISE_RE.sub("", match.group(0)).strip()
            candidates.extend(self._split_companies(candidate))
        return candidates

    def _split_companies(self, candidate: str) -> list[str]:
        '''
        purpose: 用连接词（的/与/和/旗下…）把候选片段切分成多个更干净的公司名，
                去除前缀噪声词和"关系词+为"这种修饰结构，并二次校验是否完整匹配公司名正则
        '''
        if not candidate:
            return []
        parts = [part for part in _COMPANY_CONNECTOR_RE.split(candidate) if part]
        companies: list[str] = []
        for part in parts:
            company = _FIELD_PREFIX_RE.sub("", part).strip()
            for relation in _RELATION_WORDS:
                prefix = relation + "为"
                if company.startswith(prefix):
                    company = company[len(prefix):].strip()
                    break
            if company and re.fullmatch(COMPANY_NAME_RE, company) and company not in PURE_SUFFIX_SET:
                companies.append(company)
        return companies