# Frontend Components Documentation

## Overview

Frontend menggunakan Next.js 15 dengan TypeScript dan Tailwind CSS. Semua komponen menggunakan Bahasa Indonesia.

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app directory
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Main page
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   ├── hooks/            # Custom React hooks
│   └── lib/              # Utilities and types
├── public/               # Static assets
└── package.json
```

## Components

### 1. CompanySearchForm

**File:** `frontend/src/components/CompanySearchForm.tsx`

**Purpose:** Form pencarian nama perusahaan.

**Props:**
```typescript
{
  onSubmit: (ptName: string) => void;
  isLoading: boolean;
}
```

**Features:**
- Input validation
- Disabled state saat loading
- Placeholder dalam Bahasa Indonesia

---

### 2. RiskScoreBadge

**File:** `frontend/src/components/RiskScoreBadge.tsx`

**Purpose:** Menampilkan skor risiko dengan badge warna.

**Props:**
```typescript
{
  assessment: RiskAssessment;
}
```

**Display:**
- Skor besar (0-100)
- Badge warna berdasarkan level:
  - HIJAU: Green background
  - KUNING: Yellow background
  - MERAH: Red background
- Rekomendasi dalam Bahasa Indonesia
- Breakdown komponen (Sentimen, Mentions, Hukum)

**Features:**
- Color-coded berdasarkan risk level
- Emoji indicators (✅, ⚠️, ❌)
- Component scores dengan bobot

---

### 3. ResultsChart

**File:** `frontend/src/components/ResultsChart.tsx`

**Purpose:** Menampilkan chart untuk distribusi sentimen dan komponen risiko.

**Props:**
```typescript
{
  sentiment: SentimentAnalysis;
  risk: RiskAssessment;
}
```

**Charts:**
1. **Pie Chart** - Distribusi Sentimen
   - Positif (hijau)
   - Netral (abu-abu)
   - Negatif (merah)

2. **Bar Chart** - Rincian Komponen Risiko
   - Sentimen component
   - Mentions component
   - Hukum component

**Library:** Recharts

---

### 4. LegalRecordsTable

**File:** `frontend/src/components/LegalRecordsTable.tsx`

**Purpose:** Tabel catatan hukum dengan expandable rows.

**Props:**
```typescript
{
  records: LegalRecords;
}
```

**Features:**
- Expandable rows untuk detail kasus
- Severity badges dengan warna:
  - `tinggi`: Red
  - `sedang`: Yellow
  - `rendah`: Blue
- Case type labels dalam Bahasa Indonesia
- Link ke dokumen lengkap
- Empty state jika tidak ada kasus

**Displayed Fields:**
- Nomor Kasus
- Tanggal
- Jenis (pidana, perdata, niaga, etc.)
- Tingkat Keparahan
- Judul lengkap (expanded)
- Ringkasan putusan (expanded)
- Link dokumen (expanded)

---

### 5. NewsArticlesList

**File:** `frontend/src/components/NewsArticlesList.tsx`

**Purpose:** Daftar artikel berita dengan analisis sentimen.

**Props:**
```typescript
{
  newsAnalysis?: NewsAnalysis;
}
```

**Features:**
- Sentiment badges untuk setiap artikel
- Expandable cards untuk detail
- Statistik sentimen (positif, netral, negatif)
- Link "Baca selengkapnya" membuka artikel di tab baru
- Button "Lihat detail" untuk expand/collapse
- Markdown stripping dari judul
- Visual distinction antara title dan summary

**Article Display:**
- Title: Large, bold, dark
- Summary: Smaller, lighter, in box when expanded
- Sentiment score and confidence (expanded)
- Source URL link

---

### 6. EvidenceSummary

**File:** `frontend/src/components/EvidenceSummary.tsx`

**Purpose:** Ringkasan cepat semua bukti yang dikumpulkan.

**Props:**
```typescript
{
  result: CompanyAnalysisResult;
}
```

**Summary Cards:**
1. **Berita** (📰)
   - Total articles
   - Positive/negative count

2. **Kasus Hukum** (⚖️)
   - Cases found
   - Max severity

3. **Sentimen** (💭)
   - Positive count
   - Total analyses

4. **Tingkat Risiko** (🎯)
   - Risk level badge
   - Risk score

**Key Findings Section:**
- Bullet points dengan temuan utama
- Bahasa Indonesia

---

### 7. SourceCitations

**File:** `frontend/src/components/SourceCitations.tsx`

**Purpose:** Menampilkan semua sumber referensi yang digunakan.

**Props:**
```typescript
{
  perplexitySources?: string[];
  perplexityNewsSources?: string[];
  newsArticles?: NewsArticle[];
  legalCases?: LegalCase[];
}
```

**Sections:**
1. **Referensi Perplexity** (🔍)
   - Semua sumber dari Perplexity API
   - Collapsible list
   - Numbered items

2. **Sumber Berita** (📰)
   - URL artikel dengan judul
   - Organized list

3. **Dokumen Kasus Hukum** (⚖️)
   - Case numbers dengan link
   - Case titles
   - Source URLs

**Features:**
- Collapsible sections
- Clickable links (open in new tab)
- Empty state handling

---

### 8. AnalysisLoader

**File:** `frontend/src/components/AnalysisLoader.tsx`

**Purpose:** Loading indicator saat analisis berlangsung.

**Display:**
- Spinning circle
- Message: "Menganalisis data perusahaan..."
- Estimated time: "Ini mungkin memakan waktu 15-30 detik"

---

## Custom Hooks

### useAnalysis

**File:** `frontend/src/hooks/useAnalysis.ts`

**Purpose:** State management untuk analisis perusahaan.

**Returns:**
```typescript
{
  isLoading: boolean;
  result: CompanyAnalysisResult | null;
  error: string | null;
  history: CompanyAnalysisResult[];
  analyzeCompany: (ptName: string) => Promise<void>;
  clearResult: () => void;
}
```

**Features:**
- Loading state management
- Error handling
- History tracking (last 10 analyses)
- API integration

---

## API Client

### APIClient

**File:** `frontend/src/lib/api.ts`

**Methods:**

#### `analyzeCompany(ptName: string, detailed = false)`
Mengirim request ke `/api/v1/company/analyze`

#### `healthCheck()`
Mengecek health endpoint

**Configuration:**
- Base URL: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'`
- Timeout: 120 seconds
- Error messages dalam Bahasa Indonesia

---

## Type Definitions

**File:** `frontend/src/lib/types.ts`

**Main Types:**
- `RiskLevel`: "HIJAU" | "KUNING" | "MERAH"
- `SentimentLabel`: "POSITIF" | "NETRAL" | "NEGATIF"
- `CompanyAnalysisResult`
- `NewsAnalysis`
- `NewsArticle`
- `LegalRecords`
- `RiskAssessment`
- `SentimentAnalysis`

---

## Main Page

**File:** `frontend/src/app/page.tsx`

**Layout:**
1. Header dengan judul
2. Search form
3. Loading indicator
4. Error display
5. Results (jika ada):
   - Company name & timestamp
   - Risk score badge
   - Evidence summary
   - News articles list
   - Legal records table
   - Charts
   - Source citations
   - Action buttons (New search, Export)

---

## Styling

**Framework:** Tailwind CSS

**Color Scheme:**
- Primary: Blue (buttons, links)
- Success: Green (positive sentiment, low risk)
- Warning: Yellow (neutral, medium risk)
- Danger: Red (negative sentiment, high risk)
- Text: Gray scale (800-900 for readability)

**Responsive:**
- Mobile-first design
- Grid layouts adapt to screen size
- Collapsible sections for mobile

---

## Features

✅ **Implemented:**
- Real-time analysis with loading states
- Error handling dengan pesan jelas
- Expandable sections untuk detail
- Clickable links ke sumber eksternal
- Export hasil ke JSON
- Responsive design
- Dark text dengan kontras jelas
- Markdown stripping dari titles
- Visual distinction title vs summary

