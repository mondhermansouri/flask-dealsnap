# DealSnap Deployment & Monetization Guide

## Complete Setup Instructions

### 1. Replit Backend (✅ Already Built)

Your Flask backend is ready and includes:
- AI-powered headline generation using OpenAI GPT-4o
- REST API endpoints for mobile apps
- Deal management and analytics
- Progressive Web App capabilities
- Affiliate link tracking

**Key API Endpoints:**
- `GET /api/deals` - List all deals
- `GET /api/deal/{id}` - Get specific deal
- `GET /api/categories` - Get available categories
- `GET /click/{deal_id}` - Track clicks and redirect to affiliate URL

### 2. Generate Sample Deals

1. Go to your app's admin panel: `/admin`
2. Click "Generate Sample Deals" to populate with realistic tech deals
3. The AI will automatically create catchy headlines for each deal

### 3. Android App Development

#### Option A: Flutter (Recommended for Cross-Platform)

Create a new Flutter project and use this structure:

```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  MobileAds.instance.initialize();
  runApp(DealSnapApp());
}

class DealSnapApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DealSnap',
      theme: ThemeData(
        primarySwatch: Colors.orange,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: DealsScreen(),
    );
  }
}

class Deal {
  final int id;
  final String title;
  final String aiHeadline;
  final String description;
  final double price;
  final double? originalPrice;
  final int? discountPercentage;
  final String affiliateUrl;
  final String? imageUrl;
  final String category;
  final double? rating;
  final int? numReviews;

  Deal({
    required this.id,
    required this.title,
    required this.aiHeadline,
    required this.description,
    required this.price,
    this.originalPrice,
    this.discountPercentage,
    required this.affiliateUrl,
    this.imageUrl,
    required this.category,
    this.rating,
    this.numReviews,
  });

  factory Deal.fromJson(Map<String, dynamic> json) {
    return Deal(
      id: json['id'],
      title: json['title'] ?? '',
      aiHeadline: json['ai_headline'] ?? json['title'] ?? '',
      description: json['description'] ?? '',
      price: (json['price'] ?? 0).toDouble(),
      originalPrice: json['original_price']?.toDouble(),
      discountPercentage: json['discount_percentage'],
      affiliateUrl: json['affiliate_url'] ?? '',
      imageUrl: json['image_url'],
      category: json['category'] ?? '',
      rating: json['rating']?.toDouble(),
      numReviews: json['num_reviews'],
    );
  }
}

class DealsScreen extends StatefulWidget {
  @override
  _DealsScreenState createState() => _DealsScreenState();
}

class _DealsScreenState extends State<DealsScreen> {
  List<Deal> deals = [];
  bool isLoading = true;
  String selectedCategory = 'all';
  late BannerAd _bannerAd;
  bool _isBannerAdReady = false;

  // Replace with your Replit URL
  final String apiBaseUrl = 'https://your-replit-url.replit.app';

  @override
  void initState() {
    super.initState();
    _loadBannerAd();
    fetchDeals();
  }

  void _loadBannerAd() {
    _bannerAd = BannerAd(
      adUnitId: 'ca-app-pub-3940256099942544/6300978111', // Test ad unit
      request: AdRequest(),
      size: AdSize.banner,
      listener: BannerAdListener(
        onAdLoaded: (_) {
          setState(() {
            _isBannerAdReady = true;
          });
        },
        onAdFailedToLoad: (ad, err) {
          _isBannerAdReady = false;
          ad.dispose();
        },
      ),
    );
    _bannerAd.load();
  }

  Future<void> fetchDeals() async {
    setState(() {
      isLoading = true;
    });

    try {
      final response = await http.get(
        Uri.parse('$apiBaseUrl/api/deals?category=$selectedCategory'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          deals = (data['deals'] as List)
              .map((dealJson) => Deal.fromJson(dealJson))
              .toList();
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load deals')),
      );
    }
  }

  Future<void> openDeal(Deal deal) async {
    final url = '$apiBaseUrl/click/${deal.id}';
    if (await canLaunch(url)) {
      await launch(url);
    }
  }

  @override
  void dispose() {
    _bannerAd.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('🔥 DealSnap'),
        backgroundColor: Colors.orange,
      ),
      body: Column(
        children: [
          // Category Filter
          Container(
            height: 60,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: EdgeInsets.all(8),
              children: [
                'all', 'smartphones', 'laptops', 'headphones', 
                'gaming', 'smart-home', 'accessories'
              ].map((category) => 
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 4),
                  child: FilterChip(
                    label: Text(category == 'all' ? 'All' : category),
                    selected: selectedCategory == category,
                    onSelected: (selected) {
                      setState(() {
                        selectedCategory = category;
                      });
                      fetchDeals();
                    },
                  ),
                ),
              ).toList(),
            ),
          ),
          
          // AdMob Banner
          if (_isBannerAdReady)
            Align(
              alignment: Alignment.topCenter,
              child: Container(
                width: _bannerAd.size.width.toDouble(),
                height: _bannerAd.size.height.toDouble(),
                child: AdWidget(ad: _bannerAd),
              ),
            ),
          
          // Deals List
          Expanded(
            child: isLoading
              ? Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: deals.length,
                  itemBuilder: (context, index) {
                    final deal = deals[index];
                    return Card(
                      margin: EdgeInsets.all(8),
                      child: ListTile(
                        leading: deal.imageUrl != null
                          ? Image.network(
                              deal.imageUrl!,
                              width: 60,
                              height: 60,
                              fit: BoxFit.cover,
                            )
                          : Icon(Icons.image, size: 60),
                        title: Text(
                          deal.aiHeadline,
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(deal.description),
                            SizedBox(height: 4),
                            Row(
                              children: [
                                Text(
                                  '\$${deal.price.toStringAsFixed(2)}',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green,
                                  ),
                                ),
                                if (deal.originalPrice != null) ...[
                                  SizedBox(width: 8),
                                  Text(
                                    '\$${deal.originalPrice!.toStringAsFixed(2)}',
                                    style: TextStyle(
                                      decoration: TextDecoration.lineThrough,
                                      color: Colors.grey,
                                    ),
                                  ),
                                  if (deal.discountPercentage != null)
                                    Container(
                                      margin: EdgeInsets.only(left: 8),
                                      padding: EdgeInsets.symmetric(
                                        horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: Colors.red,
                                        borderRadius: BorderRadius.circular(4),
                                      ),
                                      child: Text(
                                        '${deal.discountPercentage}% OFF',
                                        style: TextStyle(
                                          color: Colors.white,
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                ],
                              ],
                            ),
                          ],
                        ),
                        trailing: ElevatedButton(
                          onPressed: () => openDeal(deal),
                          child: Text('Get Deal'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.orange,
                          ),
                        ),
                        isThreeLine: true,
                      ),
                    );
                  },
                ),
          ),
        ],
      ),
    );
  }
}
```

**pubspec.yaml dependencies:**
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^0.13.5
  url_launcher: ^6.1.10
  google_mobile_ads: ^3.0.0
```

#### Option B: Kotlin Native Android

```kotlin
// MainActivity.kt
class MainActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var adapter: DealsAdapter
    private val deals = mutableListOf<Deal>()
    
    private val apiBaseUrl = "https://your-replit-url.replit.app"
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Initialize AdMob
        MobileAds.initialize(this) {}
        
        setupRecyclerView()
        loadDeals()
    }
    
    private fun loadDeals() {
        // Use Retrofit or OkHttp to call your API
        val client = OkHttpClient()
        val request = Request.Builder()
            .url("$apiBaseUrl/api/deals")
            .build()
            
        client.newCall(request).enqueue(object : Callback {
            override fun onResponse(call: Call, response: Response) {
                // Parse JSON and update UI
            }
            
            override fun onFailure(call: Call, e: IOException) {
                // Handle error
            }
        })
    }
}
```

### 4. Monetization Setup

#### AdMob Integration
1. Create AdMob account at https://apps.admob.com
2. Add your app and get Ad Unit IDs
3. Replace test ad units with real ones in production

#### Affiliate Links
Your app already tracks clicks through `/click/{deal_id}` endpoint. To add affiliate programs:

**Amazon Associates:**
- Sign up at https://associates.amazon.com
- Replace sample affiliate URLs with your tracking URLs
- Format: `https://amazon.com/dp/PRODUCT_ID?tag=YOUR_TAG`

**Other Programs:**
- AliExpress: https://portals.aliexpress.com
- Best Buy: https://affiliate.bestbuy.com
- Newegg: https://www.newegg.com/promotions/nepro

### 5. Push Notifications (Future)

Your service worker is already configured for push notifications. To implement:

1. Set up Firebase Cloud Messaging
2. Add notification endpoints to your Flask app
3. Send notifications for new deals

### 6. Deployment Checklist

**Replit Backend:**
- ✅ Already deployed and running
- ✅ API endpoints working
- ✅ AI headline generation active
- ✅ PWA features enabled

**Android App:**
- Use your Replit URL as `apiBaseUrl`
- Test with sample deals first
- Add real AdMob IDs before publishing
- Test affiliate link tracking

**Revenue Optimization:**
- Monitor click-through rates in admin panel
- A/B test different AI headline styles
- Add more deal sources
- Implement user favorites and notifications

### 7. Next Steps

1. **Test the API**: Visit `/api/deals` to see JSON data
2. **Generate deals**: Use admin panel to create sample deals
3. **Build mobile app**: Use the Flutter or Kotlin code above
4. **Setup monetization**: AdMob + affiliate programs
5. **Deploy**: Publish to Google Play Store

Your backend is production-ready! The AI is generating engaging headlines, and the API is perfectly structured for mobile apps.