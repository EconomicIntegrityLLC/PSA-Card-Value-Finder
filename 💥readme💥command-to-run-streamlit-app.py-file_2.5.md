cd "c:\Users\IP\Desktop\PSA" && python -m streamlit run app.py --server.port 8540

Python: app (962-1018)
  when i ran app,py....

Those warnings are harmless (they even say "can be ignored"). But the app exited - you need to run it with streamlit, not directly with python.
cd "c:\Users\IP\Desktop\PSA" && python -m streamlit run app.py --server.port 8540
ping -n 4 127.0.0.1 >nul
cd "c:\Users\IP\Desktop\PSA" && python -m streamlit run app.py --server.headless true --server.port 8541
ping -n 5 127.0.0.1 >nul
App is now running. Open http://localhost:8541 in your browser.
The key is to use streamlit run app.py instead of just python app.py. For convenience, you can also use the batch file:
Double-click START.bat in the PSA folder to launch it automatically