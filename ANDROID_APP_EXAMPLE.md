# DealSnap Android App - Complete Implementation Guide

## Flutter Implementation (Recommended)

### 1. Create New Flutter Project
```bash
flutter create dealsnap_mobile
cd dealsnap_mobile
```

### 2. Update pubspec.yaml
```yaml
name: dealsnap_mobile
description: AI-curated tech deals app

dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  url_launcher: ^6.2.1
  google_mobile_ads: ^4.0.0
  cached_network_image: ^3.3.0
  flutter_staggered_grid_view: ^0.7.0
  share_plus: ^7.2.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
```

### 3. Main App Structure (lib/main.dart)
```dart
import 'package:flutter/material.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import 'screens/deals_screen.dart';

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
        scaffoldBackgroundColor: Colors.grey[50],
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.orange,
          foregroundColor: Colors.white,
          elevation: 2,
        ),
      ),
      home: DealsScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
```

### 4. API Service (lib/services/api_service.dart)
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/deal.dart';

class ApiService {
  // Replace with your actual Replit URL
  static const String baseUrl = 'https://your-replit-url.replit.app';
  
  static Future<List<Deal>> getDeals({
    String category = 'all',
    int limit = 20,
  }) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/deals?category=$category&limit=$limit'),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['deals'] as List)
            .map((deal) => Deal.fromJson(deal))
            .toList();
      }
      throw Exception('Failed to load deals');
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
  
  static Future<List<Deal>> getFeaturedDeals({int limit = 10}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/deals/featured?limit=$limit'),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['deals'] as List)
            .map((deal) => Deal.fromJson(deal))
            .toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }
  
  static Future<List<Deal>> searchDeals(String query, {int limit = 20}) async {
    if (query.isEmpty) return [];
    
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/deals/search?q=${Uri.encodeComponent(query)}&limit=$limit'),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return (data['deals'] as List)
            .map((deal) => Deal.fromJson(deal))
            .toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }
  
  static Future<void> trackClick(int dealId) async {
    try {
      await http.get(Uri.parse('$baseUrl/click/$dealId'));
    } catch (e) {
      // Fail silently for analytics
      print('Analytics tracking failed: $e');
    }
  }
  
  static Future<List<String>> getCategories() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/api/categories'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<String>.from(data['categories']);
      }
      return ['all', 'smartphones', 'laptops', 'headphones', 'gaming'];
    } catch (e) {
      return ['all', 'smartphones', 'laptops', 'headphones', 'gaming'];
    }
  }
}
```

### 5. Deal Model (lib/models/deal.dart)
```dart
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
  final bool featured;
  final int views;
  final int clicks;

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
    this.featured = false,
    this.views = 0,
    this.clicks = 0,
  });

  factory Deal.fromJson(Map<String, dynamic> json) {
    return Deal(
      id: json['id'] ?? 0,
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
      featured: json['featured'] ?? false,
      views: json['views'] ?? 0,
      clicks: json['clicks'] ?? 0,
    );
  }
  
  bool get hasDiscount => originalPrice != null && originalPrice! > price;
  
  String get displayPrice => '\$${price.toStringAsFixed(2)}';
  
  String get displayOriginalPrice => 
      originalPrice != null ? '\$${originalPrice!.toStringAsFixed(2)}' : '';
}
```

### 6. Main Deals Screen (lib/screens/deals_screen.dart)
```dart
import 'package:flutter/material.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../services/api_service.dart';
import '../models/deal.dart';
import '../widgets/deal_card.dart';

class DealsScreen extends StatefulWidget {
  @override
  _DealsScreenState createState() => _DealsScreenState();
}

class _DealsScreenState extends State<DealsScreen> with TickerProviderStateMixin {
  List<Deal> deals = [];
  List<Deal> featuredDeals = [];
  List<String> categories = [];
  String selectedCategory = 'all';
  bool isLoading = true;
  bool isSearching = false;
  TextEditingController searchController = TextEditingController();
  late TabController tabController;
  
  late BannerAd _bannerAd;
  bool _isBannerAdReady = false;

  @override
  void initState() {
    super.initState();
    tabController = TabController(length: 3, vsync: this);
    _loadBannerAd();
    _loadInitialData();
  }

  void _loadBannerAd() {
    _bannerAd = BannerAd(
      adUnitId: 'ca-app-pub-3940256099942544/6300978111', // Test ad unit
      request: AdRequest(),
      size: AdSize.banner,
      listener: BannerAdListener(
        onAdLoaded: (_) => setState(() => _isBannerAdReady = true),
        onAdFailedToLoad: (ad, err) {
          _isBannerAdReady = false;
          ad.dispose();
        },
      ),
    );
    _bannerAd.load();
  }

  Future<void> _loadInitialData() async {
    setState(() => isLoading = true);
    
    try {
      final results = await Future.wait([
        ApiService.getDeals(category: selectedCategory),
        ApiService.getFeaturedDeals(limit: 5),
        ApiService.getCategories(),
      ]);
      
      setState(() {
        deals = results[0] as List<Deal>;
        featuredDeals = results[1] as List<Deal>;
        categories = ['all', ...results[2] as List<String>];
        isLoading = false;
      });
    } catch (e) {
      setState(() => isLoading = false);
      _showError('Failed to load deals: $e');
    }
  }

  Future<void> _loadDeals() async {
    try {
      final newDeals = await ApiService.getDeals(
        category: selectedCategory,
        limit: 30,
      );
      setState(() => deals = newDeals);
    } catch (e) {
      _showError('Failed to load deals');
    }
  }

  Future<void> _searchDeals(String query) async {
    if (query.isEmpty) {
      _loadDeals();
      return;
    }
    
    setState(() => isSearching = true);
    try {
      final searchResults = await ApiService.searchDeals(query);
      setState(() {
        deals = searchResults;
        isSearching = false;
      });
    } catch (e) {
      setState(() => isSearching = false);
      _showError('Search failed');
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  Future<void> _openDeal(Deal deal) async {
    // Track click for analytics
    ApiService.trackClick(deal.id);
    
    // Open affiliate URL
    final url = Uri.parse('${ApiService.baseUrl}/click/${deal.id}');
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  @override
  void dispose() {
    _bannerAd.dispose();
    tabController.dispose();
    searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('🔥 DealSnap'),
        bottom: TabBar(
          controller: tabController,
          tabs: [
            Tab(icon: Icon(Icons.local_fire_department), text: 'Featured'),
            Tab(icon: Icon(Icons.trending_up), text: 'All Deals'),
            Tab(icon: Icon(Icons.search), text: 'Search'),
          ],
        ),
      ),
      body: Column(
        children: [
          // AdMob Banner
          if (_isBannerAdReady)
            Container(
              alignment: Alignment.topCenter,
              child: AdWidget(ad: _bannerAd),
              width: _bannerAd.size.width.toDouble(),
              height: _bannerAd.size.height.toDouble(),
            ),
          
          Expanded(
            child: TabBarView(
              controller: tabController,
              children: [
                _buildFeaturedTab(),
                _buildAllDealsTab(),
                _buildSearchTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeaturedTab() {
    if (isLoading) return Center(child: CircularProgressIndicator());
    
    return RefreshIndicator(
      onRefresh: _loadInitialData,
      child: ListView.builder(
        padding: EdgeInsets.all(16),
        itemCount: featuredDeals.length,
        itemBuilder: (context, index) {
          return DealCard(
            deal: featuredDeals[index],
            onTap: () => _openDeal(featuredDeals[index]),
            isFeatured: true,
          );
        },
      ),
    );
  }

  Widget _buildAllDealsTab() {
    return Column(
      children: [
        // Category Filter
        Container(
          height: 60,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            itemCount: categories.length,
            itemBuilder: (context, index) {
              final category = categories[index];
              final isSelected = selectedCategory == category;
              
              return Padding(
                padding: EdgeInsets.only(right: 8),
                child: FilterChip(
                  label: Text(category == 'all' ? 'All' : category),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() => selectedCategory = category);
                    _loadDeals();
                  },
                ),
              );
            },
          ),
        ),
        
        // Deals Grid
        Expanded(
          child: isLoading 
            ? Center(child: CircularProgressIndicator())
            : RefreshIndicator(
                onRefresh: _loadDeals,
                child: GridView.builder(
                  padding: EdgeInsets.all(16),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    childAspectRatio: 0.7,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                  ),
                  itemCount: deals.length,
                  itemBuilder: (context, index) {
                    return DealCard(
                      deal: deals[index],
                      onTap: () => _openDeal(deals[index]),
                      isGrid: true,
                    );
                  },
                ),
              ),
        ),
      ],
    );
  }

  Widget _buildSearchTab() {
    return Column(
      children: [
        Padding(
          padding: EdgeInsets.all(16),
          child: TextField(
            controller: searchController,
            decoration: InputDecoration(
              hintText: 'Search deals...',
              prefixIcon: Icon(Icons.search),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              suffixIcon: searchController.text.isNotEmpty
                ? IconButton(
                    icon: Icon(Icons.clear),
                    onPressed: () {
                      searchController.clear();
                      _searchDeals('');
                    },
                  )
                : null,
            ),
            onSubmitted: _searchDeals,
            onChanged: (value) => setState(() {}),
          ),
        ),
        
        Expanded(
          child: isSearching
            ? Center(child: CircularProgressIndicator())
            : deals.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.search_off, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'Search for amazing deals!',
                        style: TextStyle(fontSize: 18, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  itemCount: deals.length,
                  itemBuilder: (context, index) {
                    return DealCard(
                      deal: deals[index],
                      onTap: () => _openDeal(deals[index]),
                    );
                  },
                ),
        ),
      ],
    );
  }
}
```

### 7. Deal Card Widget (lib/widgets/deal_card.dart)
```dart
import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/deal.dart';

class DealCard extends StatelessWidget {
  final Deal deal;
  final VoidCallback onTap;
  final bool isFeatured;
  final bool isGrid;

  const DealCard({
    Key? key,
    required this.deal,
    required this.onTap,
    this.isFeatured = false,
    this.isGrid = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: isFeatured ? 8 : 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: isGrid ? _buildGridLayout() : _buildListLayout(),
      ),
    );
  }

  Widget _buildGridLayout() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Image
        Expanded(
          flex: 3,
          child: _buildImage(),
        ),
        
        // Content
        Expanded(
          flex: 2,
          child: Padding(
            padding: EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  deal.aiHeadline,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                Spacer(),
                _buildPriceRow(),
                SizedBox(height: 4),
                _buildRating(),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildListLayout() {
    return Padding(
      padding: EdgeInsets.all(16),
      child: Row(
        children: [
          // Image
          Container(
            width: 80,
            height: 80,
            child: _buildImage(),
          ),
          
          SizedBox(width: 16),
          
          // Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  deal.aiHeadline,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                SizedBox(height: 8),
                Text(
                  deal.description,
                  style: TextStyle(color: Colors.grey[600]),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                SizedBox(height: 8),
                _buildPriceRow(),
                SizedBox(height: 4),
                _buildRating(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImage() {
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: deal.imageUrl != null
        ? CachedNetworkImage(
            imageUrl: deal.imageUrl!,
            fit: BoxFit.cover,
            placeholder: (context, url) => Container(
              color: Colors.grey[200],
              child: Center(child: CircularProgressIndicator()),
            ),
            errorWidget: (context, url, error) => Container(
              color: Colors.grey[200],
              child: Icon(Icons.image_not_supported, color: Colors.grey),
            ),
          )
        : Container(
            color: Colors.grey[200],
            child: Icon(Icons.image, color: Colors.grey),
          ),
    );
  }

  Widget _buildPriceRow() {
    return Row(
      children: [
        Text(
          deal.displayPrice,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: Colors.green[700],
          ),
        ),
        if (deal.hasDiscount) ...[
          SizedBox(width: 8),
          Text(
            deal.displayOriginalPrice,
            style: TextStyle(
              decoration: TextDecoration.lineThrough,
              color: Colors.grey,
              fontSize: 14,
            ),
          ),
          if (deal.discountPercentage != null) ...[
            SizedBox(width: 8),
            Container(
              padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
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
      ],
    );
  }

  Widget _buildRating() {
    if (deal.rating == null) return SizedBox.shrink();
    
    return Row(
      children: [
        ...List.generate(5, (index) {
          return Icon(
            index < deal.rating!.floor()
              ? Icons.star
              : index < deal.rating!.ceil()
                ? Icons.star_half
                : Icons.star_border,
            color: Colors.amber,
            size: 16,
          );
        }),
        SizedBox(width: 4),
        Text(
          '${deal.rating!.toStringAsFixed(1)} (${deal.numReviews ?? 0})',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
}
```

## Next Steps

1. **Test the Backend**: Visit your Replit app and generate sample deals
2. **Update API URL**: Replace `your-replit-url` with your actual Replit app URL
3. **Setup AdMob**: 
   - Create AdMob account
   - Add your app
   - Replace test ad units with real ones
4. **Build and Test**: Run the Flutter app and test all functionality
5. **Deploy to Play Store**: Build release APK and publish

Your DealSnap platform is now ready for passive income generation through affiliate commissions and ad revenue!