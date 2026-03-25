from unittest.mock import patch, MagicMock
from app.classifier import classify_article, keywords


class TestKeywordScoring:
    def test_unrelated_article_no_keywords(self):
        text = "The local football team won the championship last night."
        result = classify_article(text, "https://example.com/sports")

        assert result.label == "UNRELATED"
        assert result.confidence_score == 1.0
        assert result.relevant_topics == []
        assert result.url == "https://example.com/sports"

    def test_unrelated_article_few_keywords(self):
        text = "The new regulation was announced today about food safety."
        result = classify_article(text, "https://example.com/food")

        assert result.label == "UNRELATED"
        assert result.confidence_score > 0.9

    def test_unrelated_confidence_decreases_with_more_keywords(self):
        low_score_text = "A celebrity opened a restaurant."
        high_score_text = "The regulation and compliance directive on reporting oversight was discussed."

        low_result = classify_article(low_score_text, "https://example.com/1")
        high_result = classify_article(high_score_text, "https://example.com/2")

        assert low_result.confidence_score > high_result.confidence_score

    def test_unrelated_confidence_is_bounded(self):
        text = "Nothing relevant here at all."
        result = classify_article(text, "https://example.com/nothing")

        assert 0 <= result.confidence_score <= 1.0

    def test_unrelated_reasoning_is_set(self):
        text = "A cat sat on a mat."
        result = classify_article(text, "https://example.com/cat")

        assert result.reasoning == "Total number of keywords too small."

    def test_processed_at_is_set(self):
        text = "Nothing relevant."
        result = classify_article(text, "https://example.com/test")

        assert result.processed_at != ""
        assert len(result.processed_at) > 0


class TestKeywordWeights:
    def test_high_weight_keywords_score_more(self):
        # "wealth management" (weight 2) x10 = 20, triggers LLM
        # "regulation" (weight 0.25) x10 = 2.5, stays UNRELATED
        low_text = "regulation " * 10
        result = classify_article(low_text, "https://example.com/low")
        assert result.label == "UNRELATED"

    def test_all_keywords_present_in_dict(self):
        expected = [
            "wealth management", "portfolio management", "spm", "fintech",
            "analytics", "platform", "software", "dora", "mifid", "fida",
            "basel ii", "esma", "compliance", "directive", "regulation",
            "oversight", "reporting", "authorities", "regulators",
            "eu commission", "central bank"
        ]
        for kw in expected:
            assert kw in keywords, f"Missing keyword: {kw}"


class TestLLMClassification:
    @patch("app.classifier.client")
    def test_high_score_uses_gpt5_4(self, mock_client):
        mock_response = MagicMock()
        mock_response.output_parsed = MagicMock(
            label="GOOD_NEWS",
            confidence_score=0.9,
            reasoning="Positive development",
            relevant_topics=["business opportunities"],
            processed_at="",
            url=""
        )
        mock_client.responses.parse.return_value = mock_response

        # "wealth management" (weight 2) x 26 = 52 > 50
        text = "wealth management " * 26
        classify_article(text, "https://example.com/high")

        mock_client.responses.parse.assert_called_once()
        call_kwargs = mock_client.responses.parse.call_args
        assert call_kwargs.kwargs["model"] == "gpt-5.4"

    @patch("app.classifier.client")
    def test_medium_score_uses_gpt5_mini(self, mock_client):
        mock_response = MagicMock()
        mock_response.output_parsed = MagicMock(
            label="BAD_NEWS",
            confidence_score=0.7,
            reasoning="Negative development",
            relevant_topics=["regulation"],
            processed_at="",
            url=""
        )
        mock_client.responses.parse.return_value = mock_response

        # "wealth management" (weight 2) x 10 = 20, triggers mini
        text = "wealth management " * 10
        classify_article(text, "https://example.com/medium")

        mock_client.responses.parse.assert_called_once()
        call_kwargs = mock_client.responses.parse.call_args
        assert call_kwargs.kwargs["model"] == "gpt-5-mini"

    @patch("app.classifier.client")
    def test_llm_result_gets_url_and_timestamp(self, mock_client):
        mock_response = MagicMock()
        mock_response.output_parsed = MagicMock(
            label="GOOD_NEWS",
            confidence_score=0.85,
            reasoning="Good news",
            relevant_topics=["compliance"],
            processed_at="",
            url=""
        )
        mock_client.responses.parse.return_value = mock_response

        text = "wealth management " * 26
        result = classify_article(text, "https://example.com/test")

        assert result.url == "https://example.com/test"
        assert result.processed_at != ""
