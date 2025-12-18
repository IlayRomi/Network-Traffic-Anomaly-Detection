import pandas as pd
import numpy as np
from typing import Dict, Any, List

class FeatureExtractor:
    """
    רכיב זה אחראי להמיר נתונים גולמיים (מסימולטור או מרשת חיה)
    לפורמט שה-Pipeline של המודל יודע לקבל (Pandas DataFrame).
    """

    def __init__(self, feature_names_path: str = None):
        """
        אתחול המחלץ.
        :param feature_names_path: נתיב לקובץ feature_names.csv (אופציונלי לשימוש עתידי)
        """
        # רשימת הפיצ'רים שהמודל מצפה לקבל (בסדר המדויק)
        # אלו העמודות הגולמיות לפני ה-OneHotEncoding (כי ה-preprocessor יעשה את הקידוד)
        self.expected_columns = [
            'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins',
            'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root',
            'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds',
            'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
            'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
            'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count',
            'dst_host_srv_count', 'dst_host_same_srv_rate',
            'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
            'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
            'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
            'dst_host_srv_rerror_rate'
        ]

    def process_sample(self, raw_sample: Dict[str, Any]) -> pd.DataFrame:
        """
        מקבל מילון של נתונים (שורה אחת מה-CSV או פאקט מעובד)
        ומחזיר DataFrame מוכן להכנסה ל-Preprocessor.
        """
        
        # 1. יצירת DataFrame משורה בודדת
        df_sample = pd.DataFrame([raw_sample])
        
        # 2. סינון עמודות מיותרות (כמו Label או Attack Type אם הם הגיעו מהטסט)
        # אנחנו רוצים רק את הפיצ'רים שהמודל התאמן עליהם
        features_only = df_sample.reindex(columns=self.expected_columns, fill_value=0)
        
        # 3. וידוא טיפוסי נתונים (חשוב מאוד!)
        # Scikit-learn רגיש מאוד לטיפוסים. נבטיח שהמספרים הם אכן מספרים.
        numeric_cols = [c for c in self.expected_columns if c not in ['protocol_type', 'service', 'flag']]
        for col in numeric_cols:
            features_only[col] = pd.to_numeric(features_only[col], errors='coerce').fillna(0)
            
        # 4. טיפול במחרוזות (Object types)
        # מוודאים שהם String כדי שה-OneHotEncoder לא ייפול
        categorical_cols = ['protocol_type', 'service', 'flag']
        for col in categorical_cols:
            features_only[col] = features_only[col].astype(str)
            
        return features_only

    def _calculate_derived_features(self, packet_history: List[Any]):
        """
        פונקציה זו (Placeholder) תהיה בשימוש בעתיד כשנעבוד עם Scapy.
        היא תפקידה לחשב פיצ'רים כמו 'count' (כמות חיבורים בשתי שניות אחרונות)
        מתוך היסטוריית הפאקטים.
        כרגע בסימולטור - הנתונים האלו כבר מגיעים מוכנים ב-CSV.
        """
        pass