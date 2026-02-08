const express = require('express');
const cors = require('cors');
const path = require('path');

require('dotenv').config({ path: path.join(__dirname, '..', '.env') });

const app = express();
const PORT = 3001;

// CORS - Allow all origins
app.use(cors({
  origin: '*',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'x-customer-id', 'Authorization'],
}));

app.options('*', cors());
app.use(express.json());

// FIXED: Fetch both products AND prices
app.get('/api/flowglad/plans', async (req, res) => {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📋 FETCHING PRICING PLANS');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  try {
    const fetch = require('node-fetch');
    
    // Step 1: Fetch products
    console.log('📦 Fetching products...');
    const productsResponse = await fetch('https://app.flowglad.com/api/v1/products', {
      method: 'GET',
      headers: {
        'Authorization': process.env.FLOWGLAD_SECRET_KEY,
        'Content-Type': 'application/json',
      },
    });
    
    const productsData = await productsResponse.json();
    console.log('📦 Products:', productsData.data?.length || 0);
    
    // Step 2: Fetch prices
    console.log('💰 Fetching prices...');
    const pricesResponse = await fetch('https://app.flowglad.com/api/v1/prices', {
      method: 'GET',
      headers: {
        'Authorization': process.env.FLOWGLAD_SECRET_KEY,
        'Content-Type': 'application/json',
      },
    });
    
    const pricesData = await pricesResponse.json();
    console.log('💰 Prices:', pricesData.data?.length || 0);
    
    // Create a map of products by ID
    const productMap = new Map();
    (productsData.data || []).forEach(product => {
      productMap.set(product.id, product);
    });
    
    // Transform prices with product details
    const plans = (pricesData.data || []).map((price) => {
      const product = productMap.get(price.productId) || {};
      const planName = product.name || 'Unknown Plan';
      const planSlug = product.slug || '';
      
      // Define features based on plan
      let features = [];
      let description = product.description || '';
      
      if (planSlug === 'free') {
        features = ['Basic clip analysis', 'Shot type detection', 'Ball placement tracking'];
        description = description || 'Try Break Point with basic analysis';
      } else if (planSlug === 'competitor') {
        features = ['Everything in Starter', 'Advanced pattern detection', 'Behavioral insights', 'Pressure analysis', '2-month historical access'];
        description = description || 'For competitive players and league participants';
      } else if (planSlug === 'pro-monthly' || planSlug.includes('pro')) {
        features = ['Everything in Competitor', 'Deep AI reasoning', 'Full memory access', 'Opponent comparison', 'Priority processing'];
        description = description || 'Maximum depth for serious athletes';
      } else {
        features = ['Extended clip analysis', 'Rally outcome tracking', 'Basic pattern detection'];
        description = description || 'For casual players looking to improve';
      }
      
      return {
        id: price.id,
        name: planName,
        slug: planSlug,
        price: price.unitPrice / 100,
        interval: price.intervalUnit === 'month' ? 'month' : price.intervalUnit,
        description: description,
        features: features,
        popular: planSlug === 'competitor',
      };
    });
    
    console.log('✅ Transformed', plans.length, 'plans:');
    plans.forEach(p => {
      console.log(`   - ${p.name} ($${p.price}/${p.interval}) [${p.slug}]`);
    });
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    res.json({ plans });
  } catch (error) {
    console.error('❌ Failed to fetch plans:', error.message);
    console.error('Stack:', error.stack);
    res.status(500).json({ 
      error: error.message, 
      plans: [] 
    });
  }
});

// Checkout endpoint - CREATE CUSTOMER IF NEEDED
app.post('/api/flowglad/checkout', async (req, res) => {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('💳 CHECKOUT REQUEST RECEIVED');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  
  try {
    const { priceId, successUrl, cancelUrl } = req.body;
    const customerId = req.headers['x-customer-id'] || 'guest';
    
    console.log('📋 Details:');
    console.log('  Customer ID:', customerId);
    console.log('  Price ID:', priceId);
    
    const fetch = require('node-fetch');
    
    // Step 1: Try to create/get customer first
    console.log('👤 Creating customer...');
    const customerResponse = await fetch('https://app.flowglad.com/api/v1/customers', {
      method: 'POST',
      headers: {
        'Authorization': process.env.FLOWGLAD_SECRET_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customer: {
          externalId: customerId,
          email: `${customerId}@breakpoint.app`,
          name: `User ${customerId.slice(-8)}`,
        }
      }),
    });
    
    const customerData = await customerResponse.json();
    console.log('👤 Customer response:', customerResponse.status);
    
    // Step 2: Create checkout session
    console.log('🔄 Creating checkout session...');
    
    const response = await fetch('https://app.flowglad.com/api/v1/checkout-sessions', {
      method: 'POST',
      headers: {
        'Authorization': process.env.FLOWGLAD_SECRET_KEY,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        checkoutSession: {
          type: 'product',
          priceId: priceId,
          customerExternalId: customerId,
          customerEmail: `${customerId}@breakpoint.app`,
          customerName: `User ${customerId.slice(-8)}`,
          successUrl: successUrl,
          cancelUrl: cancelUrl,
        }
      }),
    });
    
    const responseText = await response.text();
    console.log('📨 Response status:', response.status);
    
    if (!response.ok) {
      console.error('❌ Flowglad API error:', responseText);
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = JSON.parse(responseText);
    
    console.log('✅ SUCCESS! Checkout session created');
    console.log('🔗 Checkout URL:', data.url);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    res.json({
      url: data.url,
      sessionId: data.checkoutSession.id,
    });
  } catch (error) {
    console.error('❌ Checkout error:', error.message);
    console.error('Stack:', error.stack);
    
    res.status(500).json({
      error: error.message,
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok',
    timestamp: new Date().toISOString(),
    secretKey: !!process.env.FLOWGLAD_SECRET_KEY,
  });
});

app.get('/', (req, res) => {
  res.json({
    name: 'Break Point Payment Server',
    status: 'running',
    endpoints: [
      '/health',
      '/api/flowglad/plans',
      '/api/flowglad/checkout'
    ]
  });
});

app.listen(PORT, () => {
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🚀 Break Point Server RUNNING');
  console.log(`📡 Local: http://localhost:${PORT}`);
  console.log(`🔑 Secret Key: ${process.env.FLOWGLAD_SECRET_KEY ? '✓' : '✗'}`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
});