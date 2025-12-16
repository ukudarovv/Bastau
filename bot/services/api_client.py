"""API client for Django REST API"""
import aiohttp
from typing import Optional, Dict, List, Any
from bot.config import API_BASE_URL


class APIClient:
    """Client for making requests to Django REST API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to API"""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                if response.status == 204:  # No content
                    return {}
                
                response_data = await response.json()
                
                if response.status >= 400:
                    error_msg = response_data.get('detail', 'Unknown error')
                    raise Exception(f"API Error {response.status}: {error_msg}")
                
                return response_data
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")
    
    # User methods
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Get user by telegram_id"""
        try:
            return await self._request('GET', f'users/telegram/{telegram_id}/')
        except Exception as e:
            if '404' in str(e) or 'not found' in str(e).lower():
                return None
            raise
    
    async def create_user(
        self,
        telegram_id: int,
        detail: str,
        geo_position_id: Optional[int] = None,
        phone_number: Optional[str] = None
    ) -> Dict:
        """Create new user"""
        data = {
            'telegram_id': telegram_id,
            'detail': detail,
            'patient': True
        }
        if geo_position_id:
            data['geo_position'] = geo_position_id
        if phone_number:
            data['phone_number'] = phone_number
        
        return await self._request('POST', 'users/', data=data)
    
    async def update_user(self, user_id: int, **kwargs) -> Dict:
        """Update user"""
        return await self._request('PATCH', f'users/{user_id}/', data=kwargs)
    
    # Category methods
    async def get_categories(self) -> List[Dict]:
        """Get all categories"""
        return await self._request('GET', 'categories/')
    
    # GeoPosition methods
    async def get_geo_positions(self) -> List[Dict]:
        """Get all geo positions (cities)"""
        return await self._request('GET', 'geopositions/')
    
    # Doctor methods
    async def get_doctors_by_category(self, category_id: int) -> List[Dict]:
        """Get doctors by category"""
        return await self._request('GET', f'users/doctors/category/{category_id}/')
    
    async def get_doctors_rating(self) -> List[Dict]:
        """Get top doctors by rating"""
        return await self._request('GET', 'users/doctors/rating/')
    
    async def get_doctor(self, doctor_id: int) -> Dict:
        """Get doctor by ID"""
        return await self._request('GET', f'users/{doctor_id}/')
    
    async def get_all_doctors(
        self,
        category_id: Optional[int] = None,
        geo_position_id: Optional[int] = None,
        clinic_id: Optional[int] = None
    ) -> List[Dict]:
        """Get all doctors with optional filters"""
        params = {}
        if category_id:
            params['category'] = category_id
        if geo_position_id:
            params['geo_position'] = geo_position_id
        if clinic_id:
            params['clinic'] = clinic_id
        
        return await self._request('GET', 'users/doctors/', params=params)
    
    # Clinic methods
    async def get_clinics_rating(self) -> List[Dict]:
        """Get top clinics by rating"""
        return await self._request('GET', 'clinics/rating/')
    
    async def get_clinic(self, clinic_id: int) -> Dict:
        """Get clinic by ID"""
        return await self._request('GET', f'clinics/{clinic_id}/')
    
    async def get_all_clinics(self) -> List[Dict]:
        """Get all clinics"""
        return await self._request('GET', 'clinics/')
    
    # Review methods
    async def create_review(
        self,
        user_id: int,
        doctor_id: int,
        rating: int,
        detail: str
    ) -> Dict:
        """Create new review"""
        data = {
            'user_id': user_id,
            'doctor_id': doctor_id,
            'rating': rating,
            'detail': detail
        }
        return await self._request('POST', 'reviews/', data=data)
    
    async def get_reviews_by_user(self, user_id: int) -> List[Dict]:
        """Get reviews by user (author)"""
        return await self._request('GET', f'reviews/user/{user_id}/')
    
    async def get_reviews_by_doctor(self, doctor_id: int) -> List[Dict]:
        """Get reviews by doctor"""
        return await self._request('GET', f'reviews/doctor/{doctor_id}/')
    
    async def check_review_exists(self, user_id: int, doctor_id: int) -> bool:
        """Check if user already has a review for this doctor"""
        reviews = await self.get_reviews_by_user(user_id)
        return any(review.get('doctor', {}).get('id') == doctor_id for review in reviews)
    
    # Support request methods
    async def create_support_request(self, user_id: int, detail: str) -> Dict:
        """Create support request"""
        data = {
            'user_id': user_id,
            'detail': detail
        }
        return await self._request('POST', 'support-requests/', data=data)

