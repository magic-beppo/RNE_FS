"""
Reusable CSV Upload Component for Dash Apps
Provides password-protected CSV upload with validation and automatic container restart
WITH LOADING SPINNER AND VISUAL FEEDBACK
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
    """A reusable CSV uploader component for Dash applications."""
    
    def __init__(self, app, csv_path, required_columns, password, 
                 backup_dir=None, container_name=None):
        """Initialize the CSV uploader component."""
        self.app = app
        self.csv_path = csv_path
        self.required_columns = required_columns
        self.password = password
        self.container_name = container_name
        
        # Auto-detect backup directory based on environment
        if backup_dir is None:
            if os.path.exists('/.dockerenv') or os.path.exists('/app'):
                self.backup_dir = '/app/backups'
            else:
                self.backup_dir = './backups'
        else:
            self.backup_dir = backup_dir
        
        # Ensure backup directory exists
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
        except PermissionError:
            self.backup_dir = './backups'
            os.makedirs(self.backup_dir, exist_ok=True)
        
        # Register callbacks
        self._register_callbacks()
    
    def get_layout(self):
        """Returns the HTML layout for the uploader component."""
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
                
                # File upload with loading spinner
                dcc.Loading(
                    id='upload-loading',
                    type='circle',  # Options: 'circle', 'default', 'cube', 'dot'
                    children=[
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
                    ]
                ),
                
                # Status messages with loading animation
                dcc.Loading(
                    id='status-loading',
                    type='default',
                    children=[html.Div(id='upload-status', style={'marginTop': '15px'})]
                ),
                
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
            if n_clicks % 2 == 1:
                return {'display': 'block', 'padding': '20px', 
                        'backgroundColor': '#f0f0f0', 'borderRadius': '8px',
                        'marginBottom': '20px'}
            else:
                return {'display': 'none'}
        
        # Display current file info
        @self.app.callback(
            Output('current-file-info', 'children'),
            [Input('show-upload-btn', 'n_clicks')]
        )
        def display_current_file_info(n_clicks):
            if not os.path.exists(self.csv_path):
                return html.Div("⚠️ No data file found!", style={'color': 'red'})
            
            try:
                file_stat = os.stat(self.csv_path)
                file_size = file_stat.st_size / 1024
                mod_time = datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                df = pd.read_csv(self.csv_path, encoding='ISO-8859-1')
                row_count = len(df)
                col_count = len(df.columns)
                
                env_info = "🐳 Running in Docker" if os.path.exists('/.dockerenv') else "💻 Running Locally"
                backup_info = f"📂 Backups: {self.backup_dir}"
                
                return html.Div([
                    html.P(f"{env_info} | {backup_info}"),
                    html.P(f"📄 File: {os.path.basename(self.csv_path)}"),
                    html.P(f"📊 Rows: {row_count:,} | Columns: {col_count}"),
                    html.P(f"💾 Size: {file_size:.2f} KB"),
                    html.P(f"🕐 Last Modified: {mod_time}"),
                ])
            except Exception as e:
                return html.Div(f"Error reading file info: {str(e)}", style={'color': 'red'})
        
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
                    html.Div("❌ Incorrect password!", 
                             style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                    html.P("Please enter the correct admin password and try again.")
                ], style={'color': 'red', 'padding': '15px', 'backgroundColor': '#ffebee', 
                         'borderRadius': '5px', 'border': '2px solid #f44336'})
            
            try:
                # Step 1: Decode file
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                # Step 2: Parse CSV with proper encoding
                try:
                    df_new = pd.read_csv(
                        io.StringIO(decoded.decode('ISO-8859-1')), 
                        dtype={'Item Code': str}
                    )
                except Exception:
                    try:
                        df_new = pd.read_csv(
                            io.StringIO(decoded.decode('utf-8')), 
                            dtype={'Item Code': str}
                        )
                    except Exception as e:
                        return html.Div([
                            html.Div("❌ Error reading CSV file", 
                                   style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                            html.P("Could not parse the file with ISO-8859-1 or UTF-8 encoding."),
                            html.P(f"Error: {str(e)[:200]}", style={'fontSize': '12px', 'fontFamily': 'monospace'})
                        ], style={'color': 'red', 'padding': '15px', 'backgroundColor': '#ffebee', 
                                'borderRadius': '5px', 'border': '2px solid #f44336'})
                
                # Step 3: Validate columns
                missing_cols = [col for col in self.required_columns if col not in df_new.columns]
                if missing_cols:
                    return html.Div([
                        html.Div("❌ Missing Required Columns", 
                               style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                        html.P(f"Missing: {', '.join(missing_cols)}"),
                        html.P(f"Expected: {', '.join(self.required_columns)}", style={'fontSize': '12px'}),
                        html.P(f"Found in file: {', '.join(df_new.columns.tolist())}", style={'fontSize': '12px'})
                    ], style={'color': 'red', 'padding': '15px', 'backgroundColor': '#ffebee', 
                            'borderRadius': '5px', 'border': '2px solid #f44336'})
                
                # Step 4: Validate data quality
                missing_pct = (df_new.isnull().sum() / len(df_new) * 100).max()
                if missing_pct > 98:
                    return html.Div([
                        html.Div("❌ Data Quality Issue", 
                               style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                        html.P(f"Too many missing values: {missing_pct:.1f}%"),
                        html.P("Please check your CSV file and try again.")
                    ], style={'color': 'red', 'padding': '15px', 'backgroundColor': '#ffebee', 
                            'borderRadius': '5px', 'border': '2px solid #f44336'})
                
                # Step 5: Create backup
                backup_success = self._create_backup()
                
                # Step 6: Save new file
                df_new.to_csv(self.csv_path, index=False, encoding='utf-8')
                
                # Step 7: Restart container
                restart_success = self._restart_container()
                
                # Success message with progress indicators
                restart_msg = (
                    "🔄 Container is restarting..." if restart_success 
                    else "⚠️ Running locally - please restart the app manually"
                )
                reload_msg = (
                    "⏳ Please wait ~15 seconds for the page to reload automatically." if restart_success
                    else "Please stop (Ctrl+C) and restart the app to see changes."
                )
                
                return html.Div([
                    # "Finished" banner at top
                    html.Div([
                        html.Span("🎉 FINISHED! ", style={'fontSize': '20px', 'fontWeight': 'bold', 'color': '#2e7d32'})
                    ], style={
                        'textAlign': 'center',
                        'padding': '10px',
                        'backgroundColor': '#c8e6c9',
                        'borderRadius': '5px',
                        'marginBottom': '15px',
                        'border': '2px solid #4caf50'
                    }),
                    
                    html.Div([
                        html.Span("✅ ", style={'fontSize': '32px', 'marginRight': '10px'}),
                        html.Span("Upload Successful!", style={'fontSize': '24px', 'fontWeight': 'bold'})
                    ], style={'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Div([
                            html.Strong("📁 File: "),
                            html.Span(filename)
                        ], style={'marginBottom': '8px'}),
                        
                        html.Div([
                            html.Strong("📊 Data: "),
                            html.Span(f"{len(df_new):,} rows × {len(df_new.columns)} columns")
                        ], style={'marginBottom': '8px'}),
                        
                        html.Div([
                            html.Strong("💾 Backup: "),
                            html.Span(backup_success)
                        ], style={'marginBottom': '8px'}),
                        
                        html.Div([
                            html.Strong("📈 Data Quality: "),
                            html.Span(f"{100 - missing_pct:.1f}% complete")
                        ], style={'marginBottom': '15px'}),
                        
                        html.Hr(style={'borderColor': '#81c784'}),
                        
                        html.Div([
                            html.P(restart_msg, style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                            html.P(reload_msg, style={'fontSize': '14px'})
                        ])
                    ])
                ], style={
                    'color': '#2e7d32',
                    'padding': '20px',
                    'backgroundColor': '#e8f5e9',
                    'borderRadius': '8px',
                    'border': '2px solid #4caf50',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
                
            except Exception as e:
                return html.Div([
                    html.Div("❌ Unexpected Error", 
                           style={'fontSize': '18px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                    html.P("An unexpected error occurred during upload."),
                    html.P(f"Error: {str(e)}", style={'fontSize': '12px', 'fontFamily': 'monospace'})
                ], style={'color': 'red', 'padding': '15px', 'backgroundColor': '#ffebee', 
                        'borderRadius': '5px', 'border': '2px solid #f44336'})
    
    def _create_backup(self):
        """Create a timestamped backup of the current CSV file."""
        if not os.path.exists(self.csv_path):
            return "No existing file to backup"
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}_{os.path.basename(self.csv_path)}"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        shutil.copy2(self.csv_path, backup_path)
        return backup_filename
    
    def _restart_container(self):
        """Restart the Docker container to reload the CSV data."""
        if not os.path.exists('/.dockerenv'):
            return False
        
        try:
            client = docker.from_env()
            
            if self.container_name is None:
                hostname = os.uname().nodename
                container = client.containers.get(hostname)
            else:
                container = client.containers.get(self.container_name)
            
            container.restart()
            return True
            
        except Exception as e:
            print(f"Container restart failed: {e}")
            return False