import logging
from flask import Blueprint, render_template, request, jsonify
from models import Dataset
from services.data_processor import DataProcessor
from services.visualization_engine import VisualizationEngine

visualization_bp = Blueprint('visualization', __name__)

def _handle_visualization_response(viz_result):
    """Helper function to handle visualization engine responses"""
    if isinstance(viz_result, dict) and 'error' in viz_result:
        return viz_result
    elif isinstance(viz_result, dict) and 'plot' in viz_result:
        return viz_result
    elif isinstance(viz_result, dict) and 'plots' in viz_result:
        return viz_result
    else:
        # Legacy format - assume it's a plotly JSON string
        return {'plot': viz_result, 'type': 'plotly'}

@visualization_bp.route('/api/generate/<int:dataset_id>')
def generate_visualizations(dataset_id):
    """Generate visualizations for dataset"""
    try:
        chart_types = request.args.getlist('charts')
        columns = request.args.getlist('columns')
        
        if not chart_types:
            return jsonify({'error': 'No chart types specified'}), 400
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset'}), 500
        
        viz_engine = VisualizationEngine()
        visualizations = {}
        
        # Generate requested visualizations
        for chart_type in chart_types:
            try:
                if chart_type == 'correlation_heatmap':
                    result = viz_engine.create_correlation_heatmap(df)
                    visualizations['correlation_heatmap'] = _handle_visualization_response(result)
                    
                elif chart_type == 'distribution_plots' and columns:
                    visualizations['distribution_plots'] = {}
                    for col in columns:
                        if col in df.columns:
                            result = viz_engine.create_distribution_plot(df, col)
                            visualizations['distribution_plots'][col] = _handle_visualization_response(result)
                            
                elif chart_type == 'box_plots' and columns:
                    visualizations['box_plots'] = {}
                    for col in columns:
                        if col in df.columns:
                            result = viz_engine.create_box_plot(df, col)
                            visualizations['box_plots'][col] = _handle_visualization_response(result)
                            
                elif chart_type == 'scatter_matrix':
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) >= 2:
                        result = viz_engine.create_scatter_matrix(df, numeric_cols[:10])
                        visualizations['scatter_matrix'] = _handle_visualization_response(result)
                    else:
                        visualizations['scatter_matrix'] = {'error': 'Insufficient numeric columns for scatter matrix'}
                        
                elif chart_type == 'pairplot':
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) >= 2:
                        result = viz_engine.create_pairplot(df, numeric_cols[:8])
                        visualizations['pairplot'] = _handle_visualization_response(result)
                    else:
                        visualizations['pairplot'] = {'error': 'Insufficient numeric columns for pairplot'}
                        
                elif chart_type == 'violin_plots' and columns:
                    visualizations['violin_plots'] = {}
                    for col in columns:
                        if col in df.columns:
                            result = viz_engine.create_violin_plot(df, col)
                            visualizations['violin_plots'][col] = _handle_visualization_response(result)
                            
                elif chart_type == 'qq_plots' and columns:
                    visualizations['qq_plots'] = {}
                    for col in columns:
                        if col in df.columns and df[col].dtype in ['int64', 'float64']:
                            result = viz_engine.create_qq_plot(df, col)
                            visualizations['qq_plots'][col] = _handle_visualization_response(result)
                            
                elif chart_type == 'bar_charts' and columns:
                    visualizations['bar_charts'] = {}
                    for col in columns:
                        if col in df.columns:
                            result = viz_engine.create_bar_chart(df, col)
                            visualizations['bar_charts'][col] = _handle_visualization_response(result)
                            
                elif chart_type == 'pie_charts' and columns:
                    visualizations['pie_charts'] = {}
                    for col in columns:
                        if col in df.columns:
                            result = viz_engine.create_pie_chart(df, col)
                            visualizations['pie_charts'][col] = _handle_visualization_response(result)
                            
                elif chart_type == 'heatmaps':
                    result = viz_engine.create_comprehensive_heatmaps(df)
                    visualizations['heatmaps'] = _handle_visualization_response(result)
                    
                elif chart_type == '3d_plots':
                    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                    if len(numeric_cols) >= 3:
                        result = viz_engine.create_3d_plots(df, numeric_cols[:3])
                        visualizations['3d_plots'] = _handle_visualization_response(result)
                    else:
                        visualizations['3d_plots'] = {'error': 'Insufficient numeric columns for 3D plots'}
                        
                else:
                    visualizations[chart_type] = {'error': f'Unknown chart type: {chart_type}'}
                    
            except Exception as chart_error:
                logging.error(f"Error generating {chart_type}: {str(chart_error)}")
                visualizations[chart_type] = {'error': str(chart_error)}
        
        return jsonify(visualizations)
        
    except Exception as e:
        logging.error(f"Visualization generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/api/comparison/<int:dataset_id>')
def comparison_visualizations(dataset_id):
    """Generate comparison visualizations between columns"""
    try:
        col1 = request.args.get('col1')
        col2 = request.args.get('col2')
        
        if not col1 or not col2:
            return jsonify({'error': 'Two columns must be specified'}), 400
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset'}), 500
        
        if col1 not in df.columns or col2 not in df.columns:
            return jsonify({'error': 'One or both specified columns not found'}), 400
        
        viz_engine = VisualizationEngine()
        comparison_viz = viz_engine.create_comparison_visualizations(df, col1, col2)
        
        return jsonify(_handle_visualization_response(comparison_viz))
        
    except Exception as e:
        logging.error(f"Comparison visualization error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@visualization_bp.route('/api/advanced/<int:dataset_id>')
def advanced_visualizations(dataset_id):
    """Generate advanced visualizations"""
    try:
        viz_type = request.args.get('type')
        
        if not viz_type:
            return jsonify({'error': 'Visualization type must be specified'}), 400
        
        dataset = Dataset.query.get_or_404(dataset_id)
        processor = DataProcessor()
        df, _ = processor.load_file(dataset.file_path)
        
        if df is None:
            return jsonify({'error': 'Could not load dataset'}), 500
        
        viz_engine = VisualizationEngine()
        
        if viz_type == 'cluster_analysis':
            result = viz_engine.create_cluster_visualizations(df)
        elif viz_type == 'pca_analysis':
            result = viz_engine.create_pca_visualizations(df)
        elif viz_type == 'time_series':
            result = viz_engine.create_time_series_visualizations(df)
        elif viz_type == 'outlier_analysis':
            result = viz_engine.create_outlier_visualizations(df)
        elif viz_type == 'feature_importance':
            result = viz_engine.create_feature_importance_plots(df)
        else:
            return jsonify({'error': f'Unknown visualization type: {viz_type}'}), 400
        
        return jsonify(_handle_visualization_response(result))
        
    except Exception as e:
        logging.error(f"Advanced visualization error: {str(e)}")
        return jsonify({'error': str(e)}), 500
