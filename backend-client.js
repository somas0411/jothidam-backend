/* backend-client.js — Jothidam Backend API Client
 *
 * Drop this file into your /js/ folder and include it in index.html AFTER app.js
 * It replaces the old client-side PDF/Excel generation with proper backend calls.
 *
 * UPDATE THE URL BELOW after deploying to Render.com
 */

const BACKEND_URL = 'https://jothidam-api.onrender.com'; // ← UPDATE after Render deploy

// ── API HELPER ────────────────────────────────────────────────────────────────

async function apiPost(endpoint, payload) {
  const res = await fetch(`${BACKEND_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res;
}

function getFormData() {
  const name  = document.getElementById('f-name')?.value?.trim()  || '';
  const dob   = document.getElementById('f-dob')?.value?.trim()   || '';
  const tob   = document.getElementById('f-tob')?.value?.trim()   || '';
  const pob   = document.getElementById('f-pob')?.value?.trim()   || '';
  const lang  = window._reportLang || 'en';
  const chartStyle = document.querySelector('input[name="chart-style"]:checked')?.value || 'south';
  return { name, dob, tob, pob, lang, chartStyle };
}

// ── TRIGGER FILE DOWNLOAD ─────────────────────────────────────────────────────

function triggerDownload(blob, filename) {
  const url  = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href  = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

// ── LOADING STATE ─────────────────────────────────────────────────────────────

function setDownloadLoading(btnId, loading, originalText) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn.disabled = true;
    btn.dataset.orig = btn.textContent;
    btn.textContent = '⏳ Generating...';
    btn.style.opacity = '0.7';
  } else {
    btn.disabled = false;
    btn.textContent = btn.dataset.orig || originalText || 'Download';
    btn.style.opacity = '1';
  }
}

// ── PDF DOWNLOAD ──────────────────────────────────────────────────────────────

async function downloadPDF() {
  const d = getFormData();
  if (!d.name || !d.dob || !d.tob || !d.pob) {
    showToast('⚠️ Please generate horoscope first');
    return;
  }

  setDownloadLoading('btn-pdf', true);
  try {
    const res  = await apiPost('/api/download/pdf', d);
    const blob = await res.blob();
    triggerDownload(blob, `Jothidam_${d.name.replace(/\s+/g,'_')}.pdf`);
    showToast('✅ PDF downloaded!');
  } catch (err) {
    console.error('PDF error:', err);
    showToast('❌ PDF generation failed. Please try again.');
  } finally {
    setDownloadLoading('btn-pdf', false);
  }
}

// ── EXCEL DOWNLOAD ────────────────────────────────────────────────────────────

async function downloadExcel() {
  const d = getFormData();
  if (!d.name || !d.dob || !d.tob || !d.pob) {
    showToast('⚠️ Please generate horoscope first');
    return;
  }

  setDownloadLoading('btn-excel', true);
  try {
    const res  = await apiPost('/api/download/excel', d);
    const blob = await res.blob();
    triggerDownload(blob, `Jothidam_${d.name.replace(/\s+/g,'_')}.xlsx`);
    showToast('✅ Excel downloaded!');
  } catch (err) {
    console.error('Excel error:', err);
    showToast('❌ Excel generation failed. Please try again.');
  } finally {
    setDownloadLoading('btn-excel', false);
  }
}

// ── RAZORPAY PAYMENT FLOW ─────────────────────────────────────────────────────

async function initiatePayment() {
  const d = getFormData();
  if (!d.name || !d.dob || !d.tob || !d.pob) {
    showToast('⚠️ Please fill all details first');
    return;
  }

  const plan  = window.PLANS?.[window.selectedPlan] || { amount: 4900, name: 'Basic' };
  const amount = plan.amount;

  try {
    // Create order on backend
    const orderRes = await apiPost('/api/create-order', { amount, currency: 'INR' });
    const order    = await orderRes.json();

    // Open Razorpay checkout
    const options = {
      key: window.RAZORPAY_KEY_ID || 'rzp_test_XXXXXXXXXX', // set in index.html
      amount:      amount,
      currency:    'INR',
      name:        'Jothidam',
      description: `${plan.name} Horoscope Report`,
      order_id:    order.order_id,
      prefill: {
        name:  d.name,
        email: '',
        contact: '',
      },
      notes: {
        name:  d.name,
        dob:   d.dob,
        tob:   d.tob,
        pob:   d.pob,
        lang:  d.lang,
        chart: d.chartStyle,
      },
      theme: { color: '#C9A03A' },
      handler: async function(response) {
        await handlePaymentSuccess(response, d);
      },
    };

    const rzp = new window.Razorpay(options);
    rzp.on('payment.failed', function(response) {
      console.error('Payment failed:', response.error);
      showToast('❌ Payment failed: ' + response.error.description);
    });
    rzp.open();

  } catch (err) {
    console.error('Payment init error:', err);
    showToast('❌ Could not initiate payment. Try again.');
  }
}

async function handlePaymentSuccess(response, formData) {
  showToast('✅ Payment successful! Generating your report...');

  try {
    // Verify payment
    const verRes = await apiPost('/api/verify-payment', {
      razorpay_order_id:   response.razorpay_order_id,
      razorpay_payment_id: response.razorpay_payment_id,
      razorpay_signature:  response.razorpay_signature,
    });
    const ver = await verRes.json();

    if (ver.verified) {
      // Auto-download PDF
      await downloadPDF();
      showToast('🎉 Report downloaded! Check your Downloads folder.');
    } else {
      showToast('⚠️ Payment verification failed. Contact support.');
    }
  } catch (err) {
    console.error('Verification error:', err);
    // Still try to give PDF (may be dev mode)
    await downloadPDF();
  }
}

// ── BACKEND HEALTH CHECK ──────────────────────────────────────────────────────

async function checkBackend() {
  try {
    const res  = await fetch(`${BACKEND_URL}/api/ping`, { method: 'GET' });
    const data = await res.json();
    console.log('✅ Backend connected:', data);
    return true;
  } catch (err) {
    console.warn('⚠️ Backend not reachable — download buttons will show error', err);
    return false;
  }
}

// Check on load (non-blocking)
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(checkBackend, 2000);
});

// ── EXPOSE GLOBALLY ───────────────────────────────────────────────────────────
window.downloadPDF    = downloadPDF;
window.downloadExcel  = downloadExcel;
window.initiatePayment = initiatePayment;

console.log('🕉 Jothidam Backend Client v2.0 loaded');
