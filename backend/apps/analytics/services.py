import logging
from typing import Dict, List, Any, Tuple, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
from decimal import Decimal
import statistics
from django.conf import settings
from apps.database.services import DatabaseService
from .models import AnalysisReport, DataInsight, BusinessMetric

# Analytics packages - will be imported when available
try:
    import numpy as np
    import pandas as pd
    from scipy import stats
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.ensemble import IsolationForest
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    # Create dummy types for when pandas is not available
    if TYPE_CHECKING:
        import pandas as pd
        import numpy as np

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Advanced analytics and data interpretation service"""

    def __init__(self):
        self.db_service = DatabaseService()

    def analyze_query_result(self, query: str, result: Dict[str, Any], analysis_type: str = 'descriptive') -> Dict[str, Any]:
        """
        Perform comprehensive analysis on query results
        """
        try:
            if not result.get('success') or not result.get('data'):
                return {'error': 'No data to analyze'}

            if not ANALYTICS_AVAILABLE:
                return {
                    'error': 'Analytics packages not available',
                    'basic_info': {
                        'row_count': len(result.get('data', [])),
                        'column_count': len(result.get('columns', [])),
                        'columns': result.get('columns', [])
                    }
                }

            # Convert to DataFrame for analysis
            df = self._result_to_dataframe(result)

            # Perform different types of analysis
            analysis = {
                'descriptive': self._descriptive_analysis(df),
                'statistical': self._statistical_analysis(df),
                'insights': self._generate_insights(df, query),
                'visualizations': self._generate_visualization_config(df),
                'recommendations': self._generate_recommendations(df, query),
                'metadata': {
                    'analysis_type': analysis_type,
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'memory_usage': df.memory_usage(deep=True).sum(),
                    'data_types': df.dtypes.to_dict()
                }
            }

            return analysis

        except Exception as e:
            logger.error(f"Error in analytics service: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}

    def _result_to_dataframe(self, result: Dict[str, Any]) -> Any:
        """Convert query result to pandas DataFrame"""
        data = result['data']
        columns = result['columns']

        if not data or not columns:
            return pd.DataFrame()

        df = pd.DataFrame(data, columns=columns)

        # Attempt to convert data types
        for col in df.columns:
            # Try to convert to numeric
            df[col] = pd.to_numeric(df[col], errors='ignore')

            # Try to convert to datetime
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], errors='ignore')
                except:
                    pass

        return df

    def _descriptive_analysis(self, df: Any) -> Dict[str, Any]:
        """Generate descriptive statistics"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        datetime_cols = df.select_dtypes(include=['datetime64']).columns

        analysis = {
            'numeric_summary': {},
            'categorical_summary': {},
            'datetime_summary': {},
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum()
        }

        # Numeric analysis
        if len(numeric_cols) > 0:
            numeric_df = df[numeric_cols]
            analysis['numeric_summary'] = {
                'describe': numeric_df.describe().to_dict(),
                'correlations': numeric_df.corr().to_dict() if len(numeric_cols) > 1 else {},
                'skewness': numeric_df.skew().to_dict(),
                'kurtosis': numeric_df.kurtosis().to_dict()
            }

        # Categorical analysis
        if len(categorical_cols) > 0:
            for col in categorical_cols:
                analysis['categorical_summary'][col] = {
                    'unique_count': df[col].nunique(),
                    'value_counts': df[col].value_counts().head(10).to_dict(),
                    'mode': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else None
                }

        # Datetime analysis
        if len(datetime_cols) > 0:
            for col in datetime_cols:
                analysis['datetime_summary'][col] = {
                    'min_date': df[col].min().isoformat() if pd.notna(df[col].min()) else None,
                    'max_date': df[col].max().isoformat() if pd.notna(df[col].max()) else None,
                    'date_range_days': (df[col].max() - df[col].min()).days if pd.notna(df[col].min()) and pd.notna(df[col].max()) else None
                }

        return analysis

    def _statistical_analysis(self, df: Any) -> Dict[str, Any]:
        """Perform advanced statistical analysis"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return {'message': 'No numeric columns for statistical analysis'}

        analysis = {
            'outliers': {},
            'normality_tests': {},
            'confidence_intervals': {},
            'hypothesis_tests': {}
        }

        for col in numeric_cols:
            data = df[col].dropna()

            if len(data) < 3:
                continue

            # Outlier detection using IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            outlier_threshold = 1.5 * IQR
            outliers = data[(data < Q1 - outlier_threshold) | (data > Q3 + outlier_threshold)]

            analysis['outliers'][col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(data)) * 100,
                'values': outliers.tolist()[:10]  # Limit to first 10
            }

            # Normality test (Shapiro-Wilk for small samples, Kolmogorov-Smirnov for larger)
            if len(data) <= 5000:
                try:
                    stat, p_value = stats.shapiro(data.sample(min(5000, len(data))))
                    analysis['normality_tests'][col] = {
                        'test': 'shapiro-wilk',
                        'statistic': float(stat),
                        'p_value': float(p_value),
                        'is_normal': p_value > 0.05
                    }
                except:
                    pass

            # Confidence intervals (95%)
            if len(data) > 1:
                mean = data.mean()
                std_err = stats.sem(data)
                ci = stats.t.interval(0.95, len(data)-1, loc=mean, scale=std_err)
                analysis['confidence_intervals'][col] = {
                    'mean': float(mean),
                    'lower_bound': float(ci[0]),
                    'upper_bound': float(ci[1]),
                    'confidence_level': 0.95
                }

        return analysis

    def _generate_insights(self, df: Any, query: str) -> List[Dict[str, Any]]:
        """Generate actionable insights from data"""
        insights = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        # Trend analysis for time series data
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            for date_col in datetime_cols:
                for num_col in numeric_cols:
                    try:
                        # Sort by date and check for trends
                        temp_df = df[[date_col, num_col]].dropna().sort_values(date_col)
                        if len(temp_df) > 3:
                            # Simple trend analysis using linear regression
                            x = np.arange(len(temp_df))
                            y = temp_df[num_col].values
                            slope, _, r_value, p_value, _ = stats.linregress(x, y)

                            if abs(r_value) > 0.3 and p_value < 0.05:
                                trend_direction = "increasing" if slope > 0 else "decreasing"
                                insights.append({
                                    'type': 'trend',
                                    'title': f"{num_col} shows {trend_direction} trend over time",
                                    'description': f"Linear correlation: {r_value:.3f}, p-value: {p_value:.3f}",
                                    'significance': abs(r_value),
                                    'metric': num_col,
                                    'value': slope
                                })
                    except:
                        continue

        # Statistical outliers
        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) > 10:
                z_scores = np.abs(stats.zscore(data))
                outliers = np.sum(z_scores > 3)
                if outliers > 0:
                    insights.append({
                        'type': 'anomaly',
                        'title': f"Found {outliers} statistical outliers in {col}",
                        'description': f"Values more than 3 standard deviations from mean",
                        'significance': min(outliers / len(data), 1.0),
                        'metric': col,
                        'value': outliers
                    })

        # High correlation insights
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            for i, col1 in enumerate(numeric_cols):
                for j, col2 in enumerate(numeric_cols[i+1:], i+1):
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.7:
                        relationship = "strong positive" if corr_value > 0 else "strong negative"
                        insights.append({
                            'type': 'correlation',
                            'title': f"{relationship} correlation between {col1} and {col2}",
                            'description': f"Correlation coefficient: {corr_value:.3f}",
                            'significance': abs(corr_value),
                            'metric': f"{col1}_vs_{col2}",
                            'value': corr_value
                        })

        # Sort insights by significance
        insights.sort(key=lambda x: x['significance'], reverse=True)

        return insights[:10]  # Return top 10 insights

    def _generate_visualization_config(self, df: Any) -> List[Dict[str, Any]]:
        """Generate visualization configurations based on data types"""
        viz_configs = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        datetime_cols = df.select_dtypes(include=['datetime64']).columns

        # Histogram for numeric columns
        for col in numeric_cols:
            viz_configs.append({
                'type': 'histogram',
                'title': f'Distribution of {col}',
                'x_column': col,
                'description': f'Shows the frequency distribution of {col} values'
            })

        # Bar chart for categorical columns
        for col in categorical_cols:
            if df[col].nunique() <= 20:  # Only for reasonable number of categories
                viz_configs.append({
                    'type': 'bar',
                    'title': f'Count by {col}',
                    'x_column': col,
                    'description': f'Shows count of records for each {col} category'
                })

        # Time series plots
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            for date_col in datetime_cols:
                for num_col in numeric_cols:
                    viz_configs.append({
                        'type': 'line',
                        'title': f'{num_col} over time',
                        'x_column': date_col,
                        'y_column': num_col,
                        'description': f'Shows how {num_col} changes over {date_col}'
                    })

        # Scatter plots for numeric correlations
        if len(numeric_cols) >= 2:
            for i, col1 in enumerate(numeric_cols):
                for col2 in numeric_cols[i+1:]:
                    viz_configs.append({
                        'type': 'scatter',
                        'title': f'{col1} vs {col2}',
                        'x_column': col1,
                        'y_column': col2,
                        'description': f'Shows relationship between {col1} and {col2}'
                    })

        return viz_configs[:8]  # Limit to 8 visualizations

    def _generate_recommendations(self, df: Any, query: str) -> List[str]:
        """Generate actionable business recommendations"""
        recommendations = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        # Data quality recommendations
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        high_missing = missing_percentage[missing_percentage > 10]

        if len(high_missing) > 0:
            recommendations.append(
                f"Data Quality Alert: {len(high_missing)} columns have >10% missing values. "
                f"Consider data cleaning for: {', '.join(high_missing.index[:3])}"
            )

        # Performance recommendations
        if len(df) > 10000:
            recommendations.append(
                "Performance: Large dataset detected. Consider using pagination, "
                "filtering, or aggregation for better query performance."
            )

        # Statistical recommendations
        for col in numeric_cols:
            data = df[col].dropna()
            if len(data) > 0:
                cv = stats.variation(data) if data.mean() != 0 else 0
                if cv > 1:
                    recommendations.append(
                        f"High Variability: {col} shows high coefficient of variation ({cv:.2f}). "
                        f"Consider investigating outliers or data segmentation."
                    )

        # Business context recommendations
        query_lower = query.lower()
        if 'customer' in query_lower:
            recommendations.append(
                "Customer Analysis: Consider segmenting customers by value, behavior, "
                "or demographics for more targeted insights."
            )
        elif 'transaction' in query_lower:
            recommendations.append(
                "Transaction Analysis: Look for seasonal patterns, fraud indicators, "
                "or customer spending behavior trends."
            )
        elif 'loan' in query_lower:
            recommendations.append(
                "Loan Analysis: Monitor default rates, payment patterns, "
                "and risk factors for portfolio management."
            )

        return recommendations[:5]  # Limit to 5 recommendations

    def calculate_business_metrics(self) -> Dict[str, Any]:
        """Calculate key business metrics for the banking domain"""
        metrics = {}

        try:
            # Customer metrics
            customer_stats = self.db_service.execute_safe_query("""
                SELECT
                    COUNT(*) as total_customers,
                    COUNT(CASE WHEN customer_segment = 'premium' THEN 1 END) as premium_customers,
                    AVG(credit_score) as avg_credit_score,
                    AVG(annual_income) as avg_income
                FROM customers
            """)

            if customer_stats['success'] and customer_stats['data']:
                data = customer_stats['data'][0]  # [total_customers, premium_customers, avg_credit_score, avg_income]
                total_customers = data[0] if len(data) > 0 else 0
                premium_customers = data[1] if len(data) > 1 else 0
                avg_credit_score = data[2] if len(data) > 2 else 0
                avg_income = data[3] if len(data) > 3 else 0

                metrics['customer_metrics'] = {
                    'total_customers': total_customers,
                    'premium_customer_rate': (premium_customers / max(total_customers, 1)) * 100,
                    'avg_credit_score': avg_credit_score,
                    'avg_annual_income': avg_income
                }

            # Account metrics
            account_stats = self.db_service.execute_safe_query("""
                SELECT
                    COUNT(*) as total_accounts,
                    SUM(balance) as total_balance,
                    AVG(balance) as avg_balance,
                    COUNT(CASE WHEN balance < 0 THEN 1 END) as negative_balance_accounts
                FROM accounts
                WHERE account_status = 'active'
            """)

            if account_stats['success'] and account_stats['data']:
                data = account_stats['data'][0]  # [total_accounts, total_balance, avg_balance, negative_balance_accounts]
                total_accounts = data[0] if len(data) > 0 else 0
                total_balance = data[1] if len(data) > 1 else 0
                avg_balance = data[2] if len(data) > 2 else 0
                negative_balance_accounts = data[3] if len(data) > 3 else 0

                metrics['account_metrics'] = {
                    'total_accounts': total_accounts,
                    'total_balance': total_balance,
                    'avg_account_balance': avg_balance,
                    'negative_balance_rate': (negative_balance_accounts / max(total_accounts, 1)) * 100
                }

            # Loan metrics
            loan_stats = self.db_service.execute_safe_query("""
                SELECT
                    COUNT(*) as total_loans,
                    SUM(loan_amount) as total_loan_amount,
                    SUM(outstanding_balance) as total_outstanding,
                    COUNT(CASE WHEN loan_status = 'default' THEN 1 END) as defaulted_loans,
                    AVG(interest_rate) as avg_interest_rate
                FROM loans
            """)

            if loan_stats['success'] and loan_stats['data']:
                data = loan_stats['data'][0]  # [total_loans, total_loan_amount, total_outstanding, defaulted_loans, avg_interest_rate]
                total_loans = data[0] if len(data) > 0 else 0
                total_loan_amount = data[1] if len(data) > 1 else 0
                total_outstanding = data[2] if len(data) > 2 else 0
                defaulted_loans = data[3] if len(data) > 3 else 0
                avg_interest_rate = data[4] if len(data) > 4 else 0

                metrics['loan_metrics'] = {
                    'total_loans': total_loans,
                    'total_loan_portfolio': total_loan_amount,
                    'total_outstanding': total_outstanding,
                    'default_rate': (defaulted_loans / max(total_loans, 1)) * 100,
                    'avg_interest_rate': avg_interest_rate
                }

            # Transaction volume (last 30 days)
            transaction_stats = self.db_service.execute_safe_query("""
                SELECT
                    COUNT(*) as transaction_count,
                    SUM(amount) as transaction_volume,
                    AVG(amount) as avg_transaction_amount
                FROM transactions
                WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
                AND status = 'completed'
            """)

            if transaction_stats['success'] and transaction_stats['data']:
                data = transaction_stats['data'][0]  # [transaction_count, transaction_volume, avg_transaction_amount]
                transaction_count = data[0] if len(data) > 0 else 0
                transaction_volume = data[1] if len(data) > 1 else 0
                avg_transaction_amount = data[2] if len(data) > 2 else 0

                metrics['transaction_metrics'] = {
                    'monthly_transaction_count': transaction_count,
                    'monthly_transaction_volume': transaction_volume,
                    'avg_transaction_amount': avg_transaction_amount
                }

            return {
                'success': True,
                'metrics': metrics,
                'calculated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating business metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def perform_cohort_analysis(self, cohort_type: str = 'customer_acquisition') -> Dict[str, Any]:
        """Perform cohort analysis on customer data"""
        try:
            if cohort_type == 'customer_acquisition':
                query = """
                    WITH customer_cohorts AS (
                        SELECT
                            c.customer_id,
                            DATE_TRUNC('month', c.created_at) as cohort_month,
                            DATE_TRUNC('month', t.transaction_date) as transaction_month,
                            COUNT(t.transaction_id) as transaction_count,
                            SUM(t.amount) as transaction_value
                        FROM customers c
                        LEFT JOIN accounts a ON c.customer_id = a.customer_id
                        LEFT JOIN transactions t ON a.account_id = t.account_id
                        WHERE c.created_at >= CURRENT_DATE - INTERVAL '12 months'
                        GROUP BY c.customer_id, cohort_month, transaction_month
                    )
                    SELECT
                        cohort_month,
                        transaction_month,
                        COUNT(DISTINCT customer_id) as active_customers,
                        SUM(transaction_count) as total_transactions,
                        SUM(transaction_value) as total_value
                    FROM customer_cohorts
                    WHERE transaction_month IS NOT NULL
                    GROUP BY cohort_month, transaction_month
                    ORDER BY cohort_month, transaction_month
                """

                result = self.db_service.execute_safe_query(query)

                if result['success']:
                    df = self._result_to_dataframe(result)

                    # Calculate retention rates
                    cohort_data = []
                    for cohort in df['cohort_month'].unique():
                        cohort_customers = df[df['cohort_month'] == cohort]
                        base_customers = cohort_customers[cohort_customers['transaction_month'] == cohort]['active_customers'].iloc[0] if len(cohort_customers[cohort_customers['transaction_month'] == cohort]) > 0 else 0

                        for _, row in cohort_customers.iterrows():
                            period_number = int((pd.to_datetime(row['transaction_month']) - pd.to_datetime(cohort)).days / 30)
                            retention_rate = (row['active_customers'] / base_customers * 100) if base_customers > 0 else 0

                            cohort_data.append({
                                'cohort_month': row['cohort_month'],
                                'period': period_number,
                                'active_customers': row['active_customers'],
                                'retention_rate': retention_rate,
                                'total_transactions': row['total_transactions'],
                                'total_value': row['total_value']
                            })

                    return {
                        'success': True,
                        'cohort_type': cohort_type,
                        'data': cohort_data,
                        'insights': self._analyze_cohort_data(cohort_data)
                    }

                return result

        except Exception as e:
            logger.error(f"Error in cohort analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_cohort_data(self, cohort_data: List[Dict]) -> List[str]:
        """Analyze cohort data and generate insights"""
        insights = []

        try:
            df = pd.DataFrame(cohort_data)

            # Average retention by period
            avg_retention = df.groupby('period')['retention_rate'].mean()

            # Find periods with significant retention drops
            for i in range(1, len(avg_retention)):
                if i < len(avg_retention) and avg_retention.iloc[i] < avg_retention.iloc[i-1] * 0.8:
                    insights.append(f"Significant retention drop in period {i}: {avg_retention.iloc[i]:.1f}% vs {avg_retention.iloc[i-1]:.1f}%")

            # Best performing cohorts
            cohort_performance = df.groupby('cohort_month')['retention_rate'].mean().sort_values(ascending=False)
            if len(cohort_performance) > 0:
                best_cohort = cohort_performance.index[0]
                insights.append(f"Best performing cohort: {best_cohort} with {cohort_performance.iloc[0]:.1f}% average retention")

            # Overall retention trend
            if len(avg_retention) > 3:
                if avg_retention.iloc[-1] > avg_retention.iloc[1]:
                    insights.append("Positive trend: Later period retention is improving")
                else:
                    insights.append("Concerning trend: Later period retention is declining")

        except Exception as e:
            logger.warning(f"Error analyzing cohort data: {str(e)}")
            insights.append("Cohort analysis completed but insight generation failed")

        return insights