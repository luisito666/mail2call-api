from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
import math
import pandas as pd
from io import BytesIO, StringIO
from datetime import datetime
from app.database.connection import get_db_connection
from app.crud.call_logs import CallLogCRUD
from app.schemas.call_logs import CallLogCreate, CallLogUpdate, CallLogResponse, PaginatedResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/call-logs", tags=["call-logs"])


@router.post("/", response_model=CallLogResponse, status_code=status.HTTP_201_CREATED)
async def create_call_log(
    call_log: CallLogCreate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    try:
        return await CallLogCRUD.create(db, call_log)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{call_log_id}", response_model=CallLogResponse)
async def get_call_log(
    call_log_id: int,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    call_log = await CallLogCRUD.get_by_id(db, call_log_id)
    if not call_log:
        raise HTTPException(status_code=404, detail="Call log not found")
    return call_log


@router.get("/", response_model=PaginatedResponse[CallLogResponse])
async def get_call_logs(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    skip = (page - 1) * per_page
    
    # Get total count and items in parallel
    total = await CallLogCRUD.get_total_count(db)
    items = await CallLogCRUD.get_all(db, skip, per_page)
    
    total_pages = math.ceil(total / per_page)
    
    return PaginatedResponse[CallLogResponse](
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/by-email-event/{email_event_id}", response_model=List[CallLogResponse])
async def get_call_logs_by_email_event(
    email_event_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await CallLogCRUD.get_by_email_event_id(db, email_event_id)


@router.get("/by-contact/{contact_id}", response_model=List[CallLogResponse])
async def get_call_logs_by_contact(
    contact_id: str,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    return await CallLogCRUD.get_by_contact_id(db, contact_id)


@router.put("/{call_log_id}", response_model=CallLogResponse)
async def update_call_log(
    call_log_id: int,
    call_log_update: CallLogUpdate,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    call_log = await CallLogCRUD.update(db, call_log_id, call_log_update)
    if not call_log:
        raise HTTPException(status_code=404, detail="Call log not found")
    return call_log


@router.delete("/{call_log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_call_log(
    call_log_id: int,
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    deleted = await CallLogCRUD.delete(db, call_log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Call log not found")


@router.get("/export/csv")
async def export_call_logs_csv(
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    """Export call logs to CSV format"""
    try:
        # Get all call logs for export
        call_logs = await CallLogCRUD.get_all_for_export(db, start_date, end_date)
        
        if not call_logs:
            raise HTTPException(status_code=404, detail="No call logs found for export")
        
        # Create DataFrame
        df = pd.DataFrame(call_logs)
        
        # Rename columns for better readability
        column_mapping = {
            'id': 'ID',
            'email_event_id': 'Email Event ID',
            'contact_id': 'Contact ID',
            'contact_name': 'Contact Name',
            'phone_number': 'Phone Number',
            'call_sid': 'Call SID',
            'status': 'Status',
            'duration': 'Duration (seconds)',
            'attempt_number': 'Attempt Number',
            'error_message': 'Error Message',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'from_email': 'From Email',
            'email_subject': 'Email Subject'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Format datetime columns
        for col in ['Created At', 'Updated At']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create CSV string
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        # Generate filename with current timestamp
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"call_logs_export_{current_time}.csv"
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(csv_content.encode('utf-8')),
            media_type='text/csv',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export/excel")
async def export_call_logs_excel(
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db=Depends(get_db_connection),
    current_user=Depends(get_current_user)
):
    """Export call logs to Excel format"""
    try:
        # Get all call logs for export
        call_logs = await CallLogCRUD.get_all_for_export(db, start_date, end_date)
        
        if not call_logs:
            raise HTTPException(status_code=404, detail="No call logs found for export")
        
        # Create DataFrame
        df = pd.DataFrame(call_logs)
        
        # Rename columns for better readability
        column_mapping = {
            'id': 'ID',
            'email_event_id': 'Email Event ID',
            'contact_id': 'Contact ID',
            'contact_name': 'Contact Name',
            'phone_number': 'Phone Number',
            'call_sid': 'Call SID',
            'status': 'Status',
            'duration': 'Duration (seconds)',
            'attempt_number': 'Attempt Number',
            'error_message': 'Error Message',
            'created_at': 'Created At',
            'updated_at': 'Updated At',
            'from_email': 'From Email',
            'email_subject': 'Email Subject'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Format datetime columns
        for col in ['Created At', 'Updated At']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Create Excel file in memory
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Call Logs', index=False)
            
            # Get workbook and worksheet to format
            workbook = writer.book
            worksheet = writer.sheets['Call Logs']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        excel_buffer.seek(0)
        
        # Generate filename with current timestamp
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"call_logs_export_{current_time}.xlsx"
        
        # Return as streaming response
        return StreamingResponse(
            BytesIO(excel_buffer.getvalue()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")