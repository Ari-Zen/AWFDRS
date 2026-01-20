# Quick Start Guide - Frontend-Backend Integration

## Test the Integration in 3 Minutes

### 1. Start Backend (Terminal 1)

```bash
cd AWFDRS

# Start infrastructure (first time or if not running)
docker-compose up -d

# Run migrations (first time only)
alembic upgrade head

# Optional: Seed test data
python scripts/seed_data.py

# Start backend
uvicorn src.awfdrs.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Backend running:** http://localhost:8000
**✅ API docs:** http://localhost:8000/docs

---

### 2. Start Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

**✅ Frontend running:** http://localhost:5173

---

### 3. Test Integration

1. **Open browser:** http://localhost:5173
2. **Click "Incidents" in sidebar**
3. **Verify:**
   - Loading spinner appears briefly
   - Incidents load from backend (or "No incidents" message if empty)
   - No errors in browser console (F12 → Console tab)
4. **Click any incident** to view details
5. **Verify:**
   - Incident detail loads with timeline
   - Related events and actions display

---

## Expected Results

### With Seeded Data

- You should see 2-3 incidents
- Each incident has:
  - Title, severity, status
  - Workflows affected
  - Timeline with events
  - Recovery actions

### Without Seeded Data

- You should see: "No incidents detected. All workflows are healthy."
- No errors in console

---

## Troubleshooting

### Backend won't start?

```bash
# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# Restart infrastructure
docker-compose down
docker-compose up -d
```

### Frontend shows errors?

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/api/v1/health
   ```
   Should return: `{"status":"ok"}`

2. **Check browser console** (F12) for specific error messages

3. **Verify `.env` file exists:**
   ```bash
   cat frontend/.env
   ```
   Should show: `VITE_API_BASE_URL=http://localhost:8000`

---

## What's Integrated?

✅ **Incidents List Page** - Fetches from backend
✅ **Incident Detail Page** - Fetches with events and actions
✅ **Error Handling** - All errors displayed with retry options
✅ **Loading States** - Spinners during API calls
✅ **CORS Configuration** - Backend accepts frontend requests

---

## What's Next?

- Integrate additional pages (Workflows, Vendors, Analytics)
- Add mutation endpoints (update status, ignore incidents)
- Implement authentication
- Add real-time updates

---

## Documentation

- **Integration Guide:** `frontend/INTEGRATION_GUIDE.md` (comprehensive technical docs)
- **Integration Summary:** `FRONTEND_BACKEND_INTEGRATION.md` (overview)
- **Backend Docs:** http://localhost:8000/docs (Swagger UI)
- **Main README:** `README.md` (project overview)

---

**Need help?** Check browser console (F12) for detailed error messages with correlation IDs.
