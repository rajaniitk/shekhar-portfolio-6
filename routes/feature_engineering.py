import logging
from flask import Blueprint, render_template, request, jsonify, current_app
from models import Dataset
from services.data_processor import DataProcessor
from services.feature_engineer import FeatureEngineer
from app import db

feature_engineering_bp = Blueprint('feature_engineering', __name__)

@feature_engineering_bp.route('/<int:dataset_id>')
def feature_engineering_page(dataset_id):
    """Feature engineering page"""
    try:
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is not None:
            # Get column information
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            all_cols = list(df.columns)
            
            # Get missing value info
            missing_info = {}
            for col in all_cols:
                missing_count = df[col].isnull().sum()
                missing_info[col] = {
                    'count': int(missing_count),
                    'percentage': float((missing_count / len(df)) * 100) if len(df) > 0 else 0
                }
            
            return render_template('feature_engineering.html', 
                                 dataset=dataset.to_dict(),
                                 numeric_columns=numeric_cols,
                                 categorical_columns=categorical_cols,
                                 all_columns=all_cols,
                                 missing_info=missing_info,
                                 data_shape=df.shape)
    except Exception as e:
        logging.error(f"Feature engineering page error: {str(e)}")
        current_app.logger.error(f"Feature engineering page error: {str(e)}")
    
    return render_template('feature_engineering.html', dataset={'id': dataset_id, 'name': 'Unknown'})

@feature_engineering_bp.route('/api/handle_missing/<int:dataset_id>', methods=['POST'])
def handle_missing_values(dataset_id):
    """Handle missing values in dataset"""
    try:
        data = request.get_json()
        strategy = data.get('strategy', 'auto')
        columns = data.get('columns', None)
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.handle_missing_values(df, strategy=strategy, columns=columns)
        
        if result.get('success'):
            # Optionally save the processed dataset
            if data.get('save_result', False):
                # Save as new dataset or update existing one
                pass
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Missing values handling error: {str(e)}")
        current_app.logger.error(f"Missing values handling error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/remove_outliers/<int:dataset_id>', methods=['POST'])
def remove_outliers(dataset_id):
    """Remove outliers from dataset"""
    try:
        data = request.get_json()
        method = data.get('method', 'auto')
        columns = data.get('columns', None)
        threshold = data.get('threshold', 3.0)
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.remove_outliers(df, method=method, columns=columns, threshold=threshold)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Outlier removal error: {str(e)}")
        current_app.logger.error(f"Outlier removal error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/feature_selection/<int:dataset_id>', methods=['POST'])
def perform_feature_selection(dataset_id):
    """Perform feature selection"""
    try:
        data = request.get_json()
        target_column = data.get('target_column')
        method = data.get('method', 'auto')
        k = data.get('k', 10)
        problem_type = data.get('problem_type', 'auto')
        
        if not target_column:
            return jsonify({'error': 'Target column is required', 'success': False}), 400
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.perform_feature_selection(df, target_column=target_column, 
                                                  method=method, k=k, problem_type=problem_type)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Feature selection error: {str(e)}")
        current_app.logger.error(f"Feature selection error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/pca/<int:dataset_id>', methods=['POST'])
def perform_pca(dataset_id):
    """Perform Principal Component Analysis"""
    try:
        data = request.get_json()
        n_components = data.get('n_components', 'auto')
        target_column = data.get('target_column', None)
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.perform_pca(df, n_components=n_components, target_column=target_column)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"PCA error: {str(e)}")
        current_app.logger.error(f"PCA error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/scale_features/<int:dataset_id>', methods=['POST'])
def scale_features(dataset_id):
    """Scale features"""
    try:
        data = request.get_json()
        method = data.get('method', 'standard')
        columns = data.get('columns', None)
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.scale_features(df, method=method, columns=columns)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Feature scaling error: {str(e)}")
        current_app.logger.error(f"Feature scaling error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/encode_categorical/<int:dataset_id>', methods=['POST'])
def encode_categorical(dataset_id):
    """Encode categorical features"""
    try:
        data = request.get_json()
        method = data.get('method', 'auto')
        columns = data.get('columns', None)
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.encode_categorical_features(df, method=method, columns=columns)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Categorical encoding error: {str(e)}")
        current_app.logger.error(f"Categorical encoding error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/polynomial_features/<int:dataset_id>', methods=['POST'])
def create_polynomial_features(dataset_id):
    """Create polynomial features"""
    try:
        data = request.get_json()
        degree = data.get('degree', 2)
        columns = data.get('columns', None)
        interaction_only = data.get('interaction_only', False)
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.create_polynomial_features(df, degree=degree, columns=columns, interaction_only=interaction_only)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Polynomial features error: {str(e)}")
        current_app.logger.error(f"Polynomial features error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/bin_features/<int:dataset_id>', methods=['POST'])
def create_binned_features(dataset_id):
    """Create binned features"""
    try:
        data = request.get_json()
        columns = data.get('columns', None)
        n_bins = data.get('n_bins', 5)
        strategy = data.get('strategy', 'uniform')
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        engineer = FeatureEngineer()
        result = engineer.create_binned_features(df, columns=columns, n_bins=n_bins, strategy=strategy)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Binned features error: {str(e)}")
        current_app.logger.error(f"Binned features error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500

@feature_engineering_bp.route('/api/data_info/<int:dataset_id>')
def get_data_info(dataset_id):
    """Get comprehensive data information"""
    try:
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset', 'success': False}), 500
        
        # Comprehensive data information
        info = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'unique_counts': df.nunique().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime_columns': df.select_dtypes(include=['datetime']).columns.tolist(),
        }
        
        # Basic statistics for numeric columns
        numeric_stats = {}
        for col in info['numeric_columns']:
            if col in df.columns:
                col_data = df[col].dropna()
                if len(col_data) > 0:
                    numeric_stats[col] = {
                        'mean': float(col_data.mean()),
                        'median': float(col_data.median()),
                        'std': float(col_data.std()),
                        'min': float(col_data.min()),
                        'max': float(col_data.max()),
                        'q25': float(col_data.quantile(0.25)),
                        'q75': float(col_data.quantile(0.75)),
                        'skewness': float(col_data.skew()),
                        'kurtosis': float(col_data.kurtosis())
                    }
        
        info['numeric_statistics'] = numeric_stats
        info['success'] = True
        
        return jsonify(info)
        
    except Exception as e:
        logging.error(f"Data info error: {str(e)}")
        current_app.logger.error(f"Data info error: {str(e)}")
        return jsonify({'error': str(e), 'success': False}), 500