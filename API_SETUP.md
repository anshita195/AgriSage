# 🌱 AgriSage API Setup Guide

This document outlines the API keys and configuration needed for AgriSage.

## Required API Keys

### 1. Google Gemini API
- **Purpose**: LLM for agricultural advice generation
- **Get Key**: https://makersuite.google.com/app/apikey
- **Environment Variable**: `GEMINI_API_KEY`

### 2. OpenWeatherMap API
- **Purpose**: Live weather forecasts (5-day)
- **Get Key**: https://openweathermap.org/api
- **Environment Variable**: `OPENWEATHER_API_KEY`
- **Plan**: Free tier (1000 calls/day)

### 3. Data.gov.in API
- **Purpose**: Official mandi prices (reliable JSON API)
- **Get Key**: https://data.gov.in/
- **Environment Variable**: `DATA_GOV_IN_API_KEY=579b464db66ec23bdd00000172446d0ce22d44d87c77605498e730e8`
- **Plan**: Free tier (register for API access)

### 4. Twilio API (Optional - for SMS)
- **Purpose**: SMS-based farmer queries
- **Get Key**: https://console.twilio.com/
- **Environment Variables**: 
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_PHONE_NUMBER`

### 5. SoilGrids ISRIC (Global Soil Data)
- **URL**: https://rest.isric.org/soilgrids/v2.0/docs
- **Free Tier**: Unlimited (no key required)
- **Data**: pH, nitrogen, organic carbon, sand/clay content

### 6. Agmarknet (Indian Market Prices)
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
