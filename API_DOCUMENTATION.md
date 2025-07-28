# DealSnap API Documentation

## Base URL
Replace `YOUR_REPLIT_URL` with your actual Replit app URL:
```
https://YOUR_REPLIT_URL.replit.app
```

## API Endpoints

### Core Deal Endpoints

#### Get All Deals
```http
GET /api/deals?category={category}&limit={limit}
```

**Parameters:**
- `category` (optional): Filter by category (`all`, `smartphones`, `laptops`, `headphones`, `gaming`, `smart-home`, `accessories`)
- `limit` (optional): Maximum number of deals to return (max 100, default 20)

**Response:**
```json
{
  "deals": [
    {
      "id": 1,
      "title": "Apple AirPods Pro (2nd Generation)",
      "ai_headline": "🔥 Save 20% on Apple AirPods Pro - Limited Time Deal!",
      "description": "Active Noise Cancellation, Transparency Mode...",
      "price": 199.99,
      "original_price": 249.99,
      "discount_percentage": 20,
      "affiliate_url": "https://amazon.com/dp/B0BDHWDR12",
      "image_url": "https://images-na.ssl-images-amazon.com/...",
      "category": "headphones",
      "source": "amazon",
      "rating": 4.5,
      "num_reviews": 15420,
      "featured": true,
      "expires_at": "2024-08-04T12:00:00Z",
      "created_at": "2024-07-28T10:30:00Z",
      "views": 1250,
      "clicks": 85
    }
  ],
  "total": 8,
  "category": "headphones"
}
```

#### Get Single Deal
```http
GET /api/deal/{deal_id}
```

**Note:** This endpoint automatically increments the view count.

#### Get Featured Deals
```http
GET /api/deals/featured?limit={limit}
```

Returns only deals marked as featured (typically the best/hottest deals).

#### Get Trending Deals
```http
GET /api/deals/trending?limit={limit}
```

Returns deals sorted by popularity (most clicks and views).

#### Search Deals
```http
GET /api/deals/search?q={query}&limit={limit}
```

**Parameters:**
- `q`: Search query (searches in title, AI headline, and description)
- `limit` (optional): Maximum results (max 50, default 20)

**Example:**
```http
GET /api/deals/search?q=bluetooth%20headphones&limit=10
```

#### Filter by Price Range
```http
GET /api/deals/price-range?min_price={min}&max_price={max}&category={category}&limit={limit}
```

**Parameters:**
- `min_price`: Minimum price (default: 0)
- `max_price`: Maximum price (default: 10000)
- `category` (optional): Filter by category
- `limit` (optional): Maximum results

**Example:**
```http
GET /api/deals/price-range?min_price=100&max_price=500&category=smartphones
```

### Analytics Endpoint

#### Get Analytics
```http
GET /api/analytics
```

**Response:**
```json
{
  "total_deals": 50,
  "active_deals": 45,
  "total_clicks": 2340,
  "total_views": 15620,
  "ctr": 14.98,
  "categories": [
    {
      "name": "smartphones",
      "deal_count": 12,
      "total_clicks": 450
    }
  ]
}
```

### Categories Endpoint

#### Get Available Categories
```http
GET /api/categories
```

**Response:**
```json
{
  "categories": [
    "electronics",
    "smartphones", 
    "laptops",
    "headphones",
    "smart-home",
    "gaming",
    "accessories"
  ]
}
```

### Click Tracking

#### Track Deal Click
```http
GET /click/{deal_id}
```

This endpoint:
1. Increments the click count for the deal
2. Logs analytics data (IP, user agent, referrer)
3. Redirects to the affiliate URL

Use this for all deal clicks to ensure proper affiliate tracking and analytics.

## Authentication

Currently, all API endpoints are public and don't require authentication. For production use, consider implementing API keys if needed.

## Rate Limiting

No rate limiting is currently implemented. Consider adding rate limiting in production based on your usage patterns.

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `404 Not Found`: Deal not found
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "error": "Deal not found",
  "status": 404
}
```

## Mobile App Integration Examples

### Flutter HTTP Client
```dart
class DealSnapAPI {
  static const String baseUrl = 'https://your-app.replit.app';
  
  static Future<List<Deal>> getDeals({String category = 'all', int limit = 20}) async {
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
  }
  
  static Future<void> trackClick(int dealId) async {
    await http.get(Uri.parse('$baseUrl/click/$dealId'));
  }
}
```

### Android Retrofit Interface
```kotlin
interface DealSnapAPI {
    @GET("api/deals")
    suspend fun getDeals(
        @Query("category") category: String = "all",
        @Query("limit") limit: Int = 20
    ): DealsResponse
    
    @GET("api/deals/featured")
    suspend fun getFeaturedDeals(@Query("limit") limit: Int = 10): DealsResponse
    
    @GET("api/deals/search")
    suspend fun searchDeals(
        @Query("q") query: String,
        @Query("limit") limit: Int = 20
    ): DealsResponse
    
    @GET("click/{dealId}")
    suspend fun trackClick(@Path("dealId") dealId: Int): ResponseBody
}
```

## Monetization Integration

### Affiliate Link Tracking
Always use the `/click/{deal_id}` endpoint instead of direct affiliate URLs to ensure:
- Proper click tracking for analytics
- Commission attribution
- User behavior insights

### Analytics for Revenue Optimization
Use the `/api/analytics` endpoint to:
- Monitor click-through rates by category
- Identify top-performing deals
- Optimize deal selection and placement

## Best Practices

1. **Cache API responses** appropriately to reduce server load
2. **Use pagination** with the limit parameter for better performance
3. **Track all clicks** through the `/click/{deal_id}` endpoint
4. **Handle errors gracefully** with proper fallbacks
5. **Respect rate limits** if implemented
6. **Update regularly** to show fresh deals to users

## Testing

You can test all endpoints using curl or any HTTP client:

```bash
# Get all deals
curl "https://your-app.replit.app/api/deals"

# Get featured deals
curl "https://your-app.replit.app/api/deals/featured?limit=5"

# Search for deals
curl "https://your-app.replit.app/api/deals/search?q=bluetooth"

# Get analytics
curl "https://your-app.replit.app/api/analytics"
```