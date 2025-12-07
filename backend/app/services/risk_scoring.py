"""
Risk scoring service.
Calculates risk scores with Bahasa Indonesia risk levels and recommendations.
"""

from typing import Dict, Any


class RiskScoringService:
    """Service for calculating credit risk scores."""
    
    SENTIMENT_WEIGHT = 0.30
    MENTIONS_WEIGHT = 0.30
    LEGAL_WEIGHT = 0.40
    
    def calculate_risk_score(
        self,
        sentiment_data: Dict[str, Any],
        legal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate final risk score from components.
        
        Formula:
        Risk = (Sentiment×0.30) + (Mentions×0.30) + (Legal×0.40)
        """
        
        sentiment_component = self._calculate_sentiment_component(sentiment_data)
        mentions_component = self._calculate_mentions_component(sentiment_data)
        legal_component = self._calculate_legal_component(legal_data)
        
        risk_score = (
            (sentiment_component * self.SENTIMENT_WEIGHT) +
            (mentions_component * self.MENTIONS_WEIGHT) +
            (legal_component * self.LEGAL_WEIGHT)
        )
        
        risk_level = self._get_risk_level(risk_score)
        recommendation = self._get_recommendation(risk_level, sentiment_component, legal_component)
        
        return {
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,  # HIJAU, KUNING, MERAH
            "sentiment_component": round(sentiment_component, 2),
            "mentions_component": round(mentions_component, 2),
            "legal_component": round(legal_component, 2),
            "details": {
                "total_texts_analyzed": sentiment_data.get('total_texts', 0),
                "positive_texts": sentiment_data.get('positive_count', 0),
                "negative_texts": sentiment_data.get('negative_count', 0),
                "legal_cases_found": legal_data.get('cases_found', 0),
                "max_case_severity": legal_data.get('max_severity', 'tidak ada'),
            },
            "recommendation": recommendation  # Bahasa Indonesia
        }
    
    def _calculate_sentiment_component(self, sentiment_data: Dict) -> float:
        """
        Sentiment risk (0-100).
        Higher negative sentiment = higher risk.
        """
        if 'error' in sentiment_data or 'valid_analyses' not in sentiment_data:
            return 50.0
        
        avg_score = sentiment_data.get('average_score', 0.5)
        # Invert: 0.0 (negative) → 100, 0.5 (neutral) → 50, 1.0 (positive) → 0
        component = (1.0 - avg_score) * 100
        return min(100, max(0, component))
    
    def _calculate_mentions_component(self, sentiment_data: Dict) -> float:
        """
        Negative mentions risk (0-100).
        Based on ratio of negative texts.
        """
        if 'valid_analyses' not in sentiment_data or sentiment_data['valid_analyses'] == 0:
            return 50.0
        
        total = sentiment_data['valid_analyses']
        negative = sentiment_data.get('negative_count', 0)
        
        # Percentage of negative mentions
        negative_ratio = (negative / total) * 100
        return min(100, max(0, negative_ratio))
    
    def _calculate_legal_component(self, legal_data: Dict) -> float:
        """
        Legal risk (0-100).
        Cases + severity = higher risk.
        Handles Bahasa Indonesia severity: tinggi, sedang, rendah, tidak ada
        """
        cases_found = legal_data.get('cases_found', 0)
        max_severity = legal_data.get('max_severity', 'tidak ada')
        
        # Base risk from case count (max 60)
        cases_risk = min(60, (cases_found / 5) * 60) if cases_found > 0 else 0
        
        # Severity bonus (Bahasa Indonesia)
        severity_map = {
            'tinggi': 40,
            'high': 40,  # Fallback for English
            'sedang': 25,
            'medium': 25,  # Fallback for English
            'rendah': 10,
            'low': 10,  # Fallback for English
            'tidak ada': 0,
            'none': 0  # Fallback for English
        }
        
        severity_risk = severity_map.get(max_severity.lower(), 0)
        component = min(100, cases_risk + severity_risk)
        
        return component
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Map score to risk level in Bahasa Indonesia."""
        if risk_score <= 30:
            return "HIJAU"
        elif risk_score <= 65:
            return "KUNING"
        else:
            return "MERAH"
    
    def _get_recommendation(
        self, 
        risk_level: str, 
        sentiment_score: float, 
        legal_score: float
    ) -> str:
        """
        Generate recommendation text in Bahasa Indonesia.
        All recommendations in Bahasa Indonesia.
        """
        
        if risk_level == "HIJAU":
            return "✅ DISARANKAN: Catatan positif. Aman untuk persetujuan kredit."
        
        elif risk_level == "KUNING":
            if legal_score > 60:
                return "⚠️ PERLU DITINJAU: Masalah hukum terdeteksi. Investigasi manual diperlukan."
            elif sentiment_score > 70:
                return "⚠️ PERLU DITINJAU: Sentimen negatif ditemukan. Due diligence lebih lanjut diperlukan."
            else:
                return "⚠️ PERLU DITINJAU: Sinyal campuran. Minta dokumentasi tambahan."
        
        else:  # MERAH
            if legal_score > 80:
                return "❌ TIDAK DISARANKAN: Riwayat hukum signifikan. Tolak aplikasi."
            else:
                return "❌ TIDAK DISARANKAN: Profil berisiko tinggi. Tolak atau minta jaminan."

