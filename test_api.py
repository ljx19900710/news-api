"""
网易新闻API测试脚本
测试接口连通性和数据准确性
"""
import json
import sys
import requests

BASE_URL = "http://localhost:5000"


def test_health():
    """测试健康检查"""
    print("=" * 60)
    print("1. 健康检查测试")
    print("=" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        data = resp.json()
        print(f"  状态码: {resp.status_code}")
        print(f"  响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        assert resp.status_code == 200
        assert data["status"] == "ok"
        print("  [PASS] 通过")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False
    return True


def test_categories():
    """测试板块列表"""
    print("\n" + "=" * 60)
    print("2. 板块列表测试")
    print("=" * 60)
    try:
        resp = requests.get(f"{BASE_URL}/api/categories", timeout=10)
        data = resp.json()
        print(f"  状态码: {resp.status_code}")
        print(f"  板块数量: {data['data']['total']}")
        print(f"  板块列表: {', '.join(data['data']['categories'][:8])}...")
        assert resp.status_code == 200
        assert len(data["data"]["categories"]) > 0
        print("  [PASS] 通过")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False
    return True


def test_news_basic():
    """测试基本新闻获取（无参数）"""
    print("\n" + "=" * 60)
    print("3. 基本新闻获取测试（默认头条，5条）")
    print("=" * 60)
    try:
        resp = requests.get(
            f"{BASE_URL}/api/news",
            params={"size": 5},
            timeout=60
        )
        data = resp.json()
        print(f"  状态码: {resp.status_code}")
        print(f"  消息: {data['message']}")
        print(f"  获取条数: {len(data['data'])}")

        if data["data"]:
            first = data["data"][0]
            print(f"\n  第一条新闻:")
            print(f"    标题: {first.get('title', 'N/A')[:60]}...")
            print(f"    来源: {first.get('source', 'N/A')}")
            print(f"    时间: {first.get('ptime', 'N/A')}")
            print(f"    图片数: {len(first.get('image_urls', []))}")
            print(f"    内容长度: {len(first.get('content', ''))}")
            print(f"    HTML长度: {len(first.get('html_content', ''))}")
            print(f"    docid: {first.get('docid', 'N/A')}")

            # 验证必填字段
            required_fields = ["title", "content", "html_content", "image_urls"]
            for field in required_fields:
                if field in first:
                    print(f"    [OK] 字段 '{field}' 存在")
                else:
                    print(f"    [FAIL] 字段 '{field}' 缺失")
                    return False

        assert resp.status_code == 200
        assert len(data["data"]) > 0
        print("\n  [PASS] 通过")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False
    return True


def test_news_with_keyword():
    """测试关键字搜索"""
    print("\n" + "=" * 60)
    print("4. 关键字搜索测试 (keyword=科技)")
    print("=" * 60)
    try:
        resp = requests.get(
            f"{BASE_URL}/api/news",
            params={"size": 10, "keyword": "科技"},
            timeout=60
        )
        data = resp.json()
        print(f"  状态码: {resp.status_code}")
        print(f"  获取条数: {len(data['data'])}")

        for i, item in enumerate(data["data"][:3]):
            title = item.get("title", "")[:50]
            print(f"  [{i+1}] {title}...")

        assert resp.status_code == 200
        print("  [PASS] 通过")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False
    return True


def test_news_with_date():
    """测试日期范围过滤"""
    print("\n" + "=" * 60)
    print("5. 日期范围过滤测试 (最近3天)")
    print("=" * 60)
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
    try:
        resp = requests.get(
            f"{BASE_URL}/api/news",
            params={
                "size": 20,
                "start_date": start_date,
                "end_date": end_date,
            },
            timeout=60
        )
        data = resp.json()
        print(f"  日期范围: {start_date} ~ {end_date}")
        print(f"  状态码: {resp.status_code}")
        print(f"  获取条数: {len(data['data'])}")

        for i, item in enumerate(data["data"][:3]):
            title = item.get("title", "")[:50]
            ptime = item.get("ptime", "")
            print(f"  [{i+1}] {ptime} - {title}...")

        assert resp.status_code == 200
        print("  [PASS] 通过")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False
    return True


def test_news_with_category():
    """测试指定板块"""
    print("\n" + "=" * 60)
    print("6. 指定板块测试 (category=军事)")
    print("=" * 60)
    try:
        resp = requests.get(
            f"{BASE_URL}/api/news",
            params={"size": 5, "category": "军事"},
            timeout=60
        )
        data = resp.json()
        print(f"  状态码: {resp.status_code}")
        print(f"  获取条数: {len(data['data'])}")

        for i, item in enumerate(data["data"][:3]):
            title = item.get("title", "")[:50]
            source = item.get("source", "")
            print(f"  [{i+1}] {title}... (来源: {source})")

        assert resp.status_code == 200
        print("  [PASS] 通过")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False
    return True


def test_error_cases():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("7. 错误处理测试")
    print("=" * 60)

    # 错误的日期格式
    try:
        resp = requests.get(
            f"{BASE_URL}/api/news",
            params={"start_date": "invalid-date"},
            timeout=10
        )
        data = resp.json()
        print(f"  错误日期格式测试 - 状态码: {resp.status_code}")
        assert resp.status_code == 400
        print("  [PASS] 正确返回400")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False

    # 404测试
    try:
        resp = requests.get(f"{BASE_URL}/nonexistent", timeout=10)
        print(f"  404测试 - 状态码: {resp.status_code}")
        assert resp.status_code == 404
        print("  [PASS] 正确返回404")
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False

    print("  [PASS] 全部通过")
    return True


def test_data_accuracy():
    """测试数据准确性"""
    print("\n" + "=" * 60)
    print("8. 数据准确性测试")
    print("=" * 60)
    try:
        resp = requests.get(
            f"{BASE_URL}/api/news",
            params={"size": 5},
            timeout=60
        )
        data = resp.json()
        items = data["data"]

        checks = []
        for item in items:
            # 标题不为空
            has_title = bool(item.get("title"))
            # 有内容或HTML内容
            has_content = bool(item.get("content") or item.get("html_content"))
            # docid不为空
            has_docid = bool(item.get("docid"))
            # 有来源
            has_source = bool(item.get("source"))
            checks.append(has_title and has_content and has_docid)

        passed = sum(checks)
        total = len(checks)
        print(f"  数据完整性: {passed}/{total}")
        print(f"  标题存在率: {sum(1 for i in items if i.get('title'))}/{total}")
        print(f"  内容存在率: {sum(1 for i in items if i.get('content') or i.get('html_content'))}/{total}")
        print(f"  docid存在率: {sum(1 for i in items if i.get('docid'))}/{total}")
        print(f"  来源存在率: {sum(1 for i in items if i.get('source'))}/{total}")

        if passed >= total * 0.8:
            print("  [PASS] 数据准确性达标")
            return True
        else:
            print(f"  [WARN] 数据准确性不足: {passed}/{total}")
            return False
    except Exception as e:
        print(f"  [FAIL] 失败: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("  网易新闻API - 连通性与数据准确性测试")
    print("=" * 60)
    print(f"  目标服务: {BASE_URL}")
    print()

    results = []

    # 依次运行所有测试
    results.append(("健康检查", test_health()))
    results.append(("板块列表", test_categories()))
    results.append(("基本新闻获取", test_news_basic()))
    results.append(("关键字搜索", test_news_with_keyword()))
    results.append(("日期范围过滤", test_news_with_date()))
    results.append(("指定板块", test_news_with_category()))
    results.append(("错误处理", test_error_cases()))
    results.append(("数据准确性", test_data_accuracy()))

    # 汇总
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "[PASS] 通过" if result else "[FAIL] 失败"
        print(f"  {status} - {name}")

    print(f"\n  总计: {passed}/{total} 通过")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
