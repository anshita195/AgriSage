# 🌱 AgriSage API Setup Guide

## Required API Keys (Free Tiers Available)

### 1. OpenWeatherMap (Weather Data)
- **URL**: https://openweathermap.org/api
- **Free Tier**: 1,000 calls/day, 5-day forecast
- **Setup**: 
  1. Sign up at openweathermap.org
  2. Get API key from dashboard
  3. Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

### 2. NASA POWER (Agricultural Data) - Optional
- **URL**: https://power.larc.nasa.gov/docs/
- **Free Tier**: Unlimited (no key required for most endpoints)
- **Data**: Temperature, precipitation, solar radiation, humidity

### 3. SoilGrids ISRIC (Global Soil Data)
- **URL**: https://rest.isric.org/soilgrids/v2.0/docs
- **Free Tier**: Unlimited (no key required)
- **Data**: pH, nitrogen, organic carbon, sand/clay content

### 4. Agmarknet (Indian Market Prices)
- **URL**: https://agmarknet.gov.in
- **Free Tier**: CSV downloads available
- **Data**: Daily commodity prices, mandi data

## Environment Variables

Create `.env` file in project root:

```env
# Required for weather data
OPENWEATHER_API_KEY=your_openweather_key

# Optional for enhanced features
NASA_POWER_API_KEY=optional_nasa_key
GEMINI_API_KEY=your_gemini_key

# SMS (for production)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+15005550006
```

## API Endpoints Used

### Weather (OpenWeatherMap)
```
GET https://api.openweathermap.org/data/2.5/forecast
Parameters: lat, lon, appid, units=metric, cnt=5
```

### Soil (SoilGrids)
```
GET https://rest.isric.org/soilgrids/v2.0/properties/query
Parameters: lon, lat, property=[phh2o,nitrogen,soc], depth=[0-5cm]
```

### Agricultural Data (NASA POWER)
```
GET https://power.larc.nasa.gov/api/temporal/daily/point
Parameters: parameters, community=AG, longitude, latitude, start, end
```

### Market Data (Agmarknet)
```
GET https://agmarknet.gov.in/Others/profile.aspx?ss=1&mi=3
Format: CSV download
```

## Data Sources Comparison

| Source | Reliability | Coverage | Update Frequency | API Limits |
|--------|-------------|----------|------------------|------------|
| OpenWeatherMap | ⭐⭐⭐⭐⭐ | Global | Hourly | 1K/day free |
| SoilGrids | ⭐⭐⭐⭐⭐ | Global | Static | Unlimited |
| NASA POWER | ⭐⭐⭐⭐ | Global | Daily | Unlimited |
| Agmarknet | ⭐⭐⭐ | India only | Daily | CSV only |

## Fallback Strategy

If APIs fail, system uses:
- **Weather**: Local averages for region
- **Soil**: SoilGrids cached data
- **Markets**: Historical price trends
- **Safety**: Conservative advice only

## Testing APIs

```bash
# Test all APIs
python services/ingestion/reliable_api_fetcher.py

# Test individual components
python -c "from services.ingestion.reliable_api_fetcher import ReliableAPIFetcher; f=ReliableAPIFetcher(); print(f.fetch_openweather_data([{'district':'Delhi','lat':28.6,'lon':77.2}]))"
```

## Production Considerations

1. **Rate Limiting**: Implement exponential backoff
2. **Caching**: Cache responses for 1-6 hours
3. **Monitoring**: Track API success rates
4. **Costs**: Monitor usage to stay within free tiers
5. **Backup**: Multiple data sources for critical data
