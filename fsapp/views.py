from django.shortcuts import render
from django.http import HttpResponse
import io
import pandas as pd
import sys
from pathlib import Path
import io

# Import hàm price_stock từ file finance_df.py
from static.finance_py.finance_df import *
from static.finance_py.const import *

def financial_statement(request):
    if request.method == "POST":
        symbol = request.POST.get('symbol')
        type = request.POST.get('type')
        year = request.POST.get('year')
        timely = request.POST.get('timely')
        action = request.POST.get('action')

        # Validate required fields
        if not symbol or not type or not year or not timely:
            error_msg = 'Please fill in all required fields: Symbol, Type, Year, and Timely!'
            return render(request, 'Main/home.html', {
                'error': error_msg,
                'symbol': symbol,
                'type': type,
                'year': year,
                'timely': timely,
            })
        
        df = financial_report(symbol, type, year, timely)

        # No data found
        if df.empty:
            error_msg = f'No data found for {symbol} in the given date range!'
            return render(request, 'Main/home.html', {
                'error': error_msg,
                'symbol': symbol,
                'type': type,
                'year': year,
                'timely': timely,
            })

        # Handle action: get_data
        if action == "get_data":
            data_list = df.to_dict('records')
            return render(request, 'Main/home.html', {
                'data': data_list,
                'symbol': symbol,
                'type': type,
                'year': year,
                'timely': timely,
            })

        # Handle action: download
        elif action == "download":
            # Làm sạch dữ liệu DataFrame trước khi export
            df_clean = df.replace(r'\n|\r', ' ', regex=True)  # Xóa các ký tự xuống dòng
            # df_clean = df_clean.applymap(lambda x: x.strip() if isinstance(x, str) else x)  # Xóa khoảng trắng dư

            # Tạo file CSV
            response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
            response['Content-Disposition'] = f'attachment; filename="financial_{symbol}_{type}_{year}_{timely}.csv"'

            # Ghi dữ liệu vào file CSV
            output = io.StringIO()
            df_clean.to_csv(output, index=False, encoding="utf-8", sep=";", decimal=",")

            # df_clean.to_csv(
            #     path_or_buf=output,
            #     index=False,
            #     # sep=",",  # Sử dụng dấu phẩy là chuẩn CSV
            #     encoding="utf-8-sig",
            #     sep=";",
            #     decimal=","
            # )
            
            # Ghi dữ liệu từ StringIO vào HttpResponse
            response.write(output.getvalue())
            return response

        # Invalid action
        else:
            error_msg = "Invalid action. Please select a valid action: Get Data or Download."
            return render(request, 'Main/home.html', {
                'error': error_msg,
                'symbol': symbol,
                'type': type,
                'year': year,
                'timely': timely,
            })

    # Default GET request or no action
    return render(request, 'Main/home.html')
