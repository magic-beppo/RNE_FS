"""
Reusable CSV Upload Component for Dash Apps
Provides password-protected CSV upload with validation and automatic container restart
"""

import os
import shutil
import base64
import io
from datetime import datetime
import pandas as pd
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import docker


class CSVUploader:
    """
    A reusable CSV uploader component for Dash applications.
    
    Features:
    - Password-protected upload interface
    - CSV structure validation
    - Automatic backup creation
    - Container auto-restart after upload
    
    Usage:
        uploader = CSVUploader(
            app=app,
            csv_path='/app/FS_selection.csv',
            required_columns=['Area', 'Year', 'Item', 'Value', 'Unit'],
            password='your_secure_password'
        )
        
        # Add to layout
        app.layout = html.Div([
            uploader.get_layout(),
            # ... rest of your layout
        ])
    """
    
    def __init__(self, app, csv_path, required_columns, password, 
                 backup_dir=None, container_name=None):
        """
        Initialize the CSV uploader component.
        
        Args:
            app: Dash app instance
            csv_path: Full path to CSV file that will be replaced
            required_columns: List of required column names
            password: Password for upload access
            backup_dir: Directory to store backup files (auto-detected if None)
            container_name: Docker container name (auto-detected if None)
        """
        self.app = app
        self.csv_path = csv_path
        self.required_columns = required_columns
        self.password = password
        self.container_name = container_name
        
        # Auto-detect backup directory based on environment
        if backup_dir is None:
            # Check if running in Docker container
            if os.path.exists('/.dockerenv') or os.path.exists('/app'):
                self.backup_dir = '/app/backups'
            else:
                # Running locally - use relative path
                self.backup_dir = './backups'
        else:
            self.backup_dir = backup_dir
        
        # Ensure backup directory exists (with proper error handling)
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
        except PermissionError:
            # Fallback to local directory if can't create in /app
            self.backup_dir = './backups'
            os.makedirs(self.backup_dir, exist_ok=True)
        
        # Register callbacks
        self._register_callbacks()
    
    def get_layout(self):
        """
        Returns the HTML layout for the uploader component.
        Add this to your Dash app layout.
        """
        return html.Div([
            html.Div([
                html.Button(
                    "🔧 Admin: Update Data", 
                    id='show-upload-btn',
                    n_clicks=0,
                    style={
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'padding': '10px 20px',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontSize': '14px',
                        'marginBottom': '10px'
                    }
                ),
            ]),
            
            html.Div([
                # Password input
                html.Div([
                    html.Label("Admin Password:", style={'fontWeight': 'bold'}),
                    dcc.Input(
                        id='admin-password',
                        type='password',
                        placeholder='Enter admin password',
                        style={'width': '300px', 'padding': '8px', 'marginLeft': '10px'}
                    ),
                ], style={'marginBottom': '15px'}),
                
                # File upload
                dcc.Upload(
                    id='upload-csv',
                    children=html.Div([
                        '📁 Drag and Drop or ',
                        html.A('Select CSV File', style={'color': '#4CAF50', 'fontWeight': 'bold'})
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '2px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'borderColor': '#4CAF50',
                        'textAlign': 'center',
                        'backgroundColor': '#f9f9f9',
                        'cursor': 'pointer'
                    },
                    multiple=False
                ),
                
                # Status messages
                html.Div(id='upload-status', style={'marginTop': '15px'}),
                
                # Current file info
                html.Div([
                    html.Hr(),
                    html.H4("Current Data File Info:"),
                    html.Div(id='current-file-info')
                ], style={'marginTop': '20px'}),
                
            ], id='upload-container', style={'display': 'none', 'padding': '20px', 
                                             'backgroundColor': '#f0f0f0', 
                                             'borderRadius': '8px',
                                             'marginBottom': '20px'})
        ])
    
    def _register_callbacks(self):
        """Register all callbacks for the uploader component"""
        
        # Toggle upload container visibility
        @self.app.callback(
            Output('upload-container', 'style'),
            [Input('show-upload-btn', 'n_clicks')],
            [State('upload-container', 'style')]
        )
        def toggle_upload_container(n_clicks, current_style):
            if n_clicks % 2 == 1:  # Odd clicks = show
                return {'display': 'block', 'padding': '20px', 
                        'backgroundColor': '#f0f0f0', 'borderRadius': '8px',
                        'marginBottom': '20px'}
            else:  # Even clicks = hide
                return {'display': 'none'}
        
        # Display current file info
        @self.app.callback(
            Output('current-file-info', 'children'),
            [Input('show-upload-btn', 'n_clicks')]
        )
        def display_current_file_info(n_clicks):
            if not os.path.exists(self.csv_path):
                return html.Div("⚠️ No data file found!", style={'color': 'red'})
            
            # Get file stats
            file_stat = os.stat(self.csv_path)
            file_size = file_stat.st_size / 1024  # KB
            mod_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # Get row count - use same encoding as original file
            try:
                df = pd.read_csv(self.csv_path, encoding='ISO-8859-1')
                row_count = len(df)
                col_count = len(df.columns)
            except:
                row_count = "Error reading file"
                col_count = "Error reading file"
            
            # Show environment info
            env_info = "🐳 Running in Docker" if os.path.exists('/.dockerenv') else "💻 Running Locally"
            backup_info = f"📂 Backups: {self.backup_dir}"
            
            return html.Div([
                html.P(f"{env_info} | {backup_info}"),
                html.P(f"📄 File: {os.path.basename(self.csv_path)}"),
                html.P(f"📊 Rows: {row_count:,} | Columns: {col_count}"),
                html.P(f"💾 Size: {file_size:.2f} KB"),
                html.P(f"🕐 Last Modified: {mod_time}"),
            ])
        
        # Handle CSV upload
        @self.app.callback(
            Output('upload-status', 'children'),
            [Input('upload-csv', 'contents')],
            [State('upload-csv', 'filename'),
             State('admin-password', 'value')]
        )
        def handle_csv_upload(contents, filename, password):
            if contents is None:
                return ""
            
            # Check password
            if password != self.password:
                return html.Div([
                    "❌ Incorrect password!",
                ], style={'color': 'red', 'fontWeight': 'bold'})
            
            try:
                # Parse uploaded file with proper encoding
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                # Try ISO-8859-1 encoding first (matches your original data)
                try:
                    df_new = pd.read_csv(
                        io.StringIO(decoded.decode('ISO-8859-1')), 
                        dtype={'Item Code': str}
                    )
                except Exception as e1:
                    # Fallback to UTF-8 if ISO-8859-1 fails
                    try:
                        df_new = pd.read_csv(
                            io.StringIO(decoded.decode('utf-8')), 
                            dtype={'Item Code': str}
                        )
                    except Exception as e2:
                        return html.Div([
                            f"❌ Error reading CSV file. Tried ISO-8859-1 and UTF-8 encoding.",
                            html.Br(),
                            f"ISO-8859-1 error: {str(e1)}",
                            html.Br(),
                            f"UTF-8 error: {str(e2)}"
                        ], style={'color': 'red', 'fontWeight': 'bold'})
                
                # Validation 1: Check required columns
                missing_cols = [col for col in self.required_columns if col not in df_new.columns]
                if missing_cols:
                    return html.Div([
                        f"❌ Validation Error: Missing required columns: {', '.join(missing_cols)}",
                        html.Br(),
                        f"Expected columns: {', '.join(self.required_columns)}",
                        html.Br(),
                        f"Found columns: {', '.join(df_new.columns.tolist())}"
                    ], style={'color': 'red', 'fontWeight': 'bold'})
                
                # Validation 2: Check data types and basic integrity
                validation_results = self._validate_dataframe(df_new)
                if not validation_results['valid']:
                    return html.Div([
                        f"❌ Validation Error: {validation_results['message']}"
                    ], style={'color': 'red', 'fontWeight': 'bold'})
                
                # Create backup of existing file
                backup_success = self._create_backup()
                
                # Save new file with UTF-8 encoding (standard for web)
                df_new.to_csv(self.csv_path, index=False, encoding='utf-8')
                
                # Trigger container restart (only in Docker)
                restart_success = self._restart_container()
                
                # Success message
                restart_msg = (
                    "🔄 Container restart initiated..." if restart_success 
                    else "⚠️ Running locally - please restart app manually to see changes"
                )
                reload_msg = (
                    "The page will reload automatically in a few seconds." if restart_success
                    else "Please restart the app to load new data."
                )
                
                return html.Div([
                    html.P("✅ Upload Successful!", style={'color': 'green', 'fontWeight': 'bold', 'fontSize': '16px'}),
                    html.P(f"📁 File: {filename}"),
                    html.P(f"📊 Rows: {len(df_new):,} | Columns: {len(df_new.columns)}"),
                    html.P(f"💾 Backup created: {backup_success}"),
                    html.P(restart_msg),
                    html.P(reload_msg),
                ], style={'color': 'green'})
                
            except Exception as e:
                return html.Div([
                    f"❌ Unexpected Error: {str(e)}"
                ], style={'color': 'red', 'fontWeight': 'bold'})
    
    def _validate_dataframe(self, df):
        """
        Validate the uploaded dataframe structure and data types.
        
        Returns:
            dict: {'valid': bool, 'message': str}
        """
        # Check if dataframe is empty
        if len(df) == 0:
            return {'valid': False, 'message': 'CSV file is empty'}
        
        # Check for excessive missing values (relaxed to 98%)
        missing_pct = (df.isnull().sum() / len(df) * 100).max()
        if missing_pct > 98:
            return {'valid': False, 'message': f'Too many missing values ({missing_pct:.1f}%)'}
        
        # Validate specific columns if they exist
        if 'Value' in df.columns:
            # Check if Value column can be converted to numeric
            try:
                pd.to_numeric(df['Value'], errors='coerce')
            except:
                return {'valid': False, 'message': 'Value column contains invalid data'}
        
        if 'Year' in df.columns:
            # Check if Year is reasonable (allow formats like "2020" or "2020-2021")
            years = df['Year'].dropna().astype(str)
            if len(years) > 0 and not years.str.match(r'^\d{4}(-\d{4})?$').all():
                return {'valid': False, 'message': 'Year column contains invalid format'}
        
        return {'valid': True, 'message': 'Validation passed'}
    
    def _create_backup(self):
        """
        Create a timestamped backup of the current CSV file.
        
        Returns:
            str: Backup filename
        """
        if not os.path.exists(self.csv_path):
            return "No existing file to backup"
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}_{os.path.basename(self.csv_path)}"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        shutil.copy2(self.csv_path, backup_path)
        return backup_filename
    
    def _restart_container(self):
        """
        Restart the Docker container to reload the CSV data.
        Only works when running inside Docker container.
        
        Returns:
            bool: True if restart initiated successfully
        """
        # Check if running in Docker
        if not os.path.exists('/.dockerenv'):
            print("Not running in Docker - skipping container restart")
            return False
        
        try:
            client = docker.from_env()
            
            # Auto-detect container name if not provided
            if self.container_name is None:
                # Get current container hostname (container ID)
                hostname = os.uname().nodename
                container = client.containers.get(hostname)
            else:
                container = client.containers.get(self.container_name)
            
            # Restart container
            container.restart()
            return True
            
        except Exception as e:
            print(f"Container restart failed: {e}")
            return False