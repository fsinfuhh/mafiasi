from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone

class TokensExceeded(Exception):
    def __init__(self, time_available):
        self.time_available = time_available

class TokenBucket(models.Model):
    identifier = models.CharField(max_length=30)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    max_tokens = models.IntegerField()
    fill_rate = models.FloatField()
    tokens = models.FloatField(default=0.0)
    last_updated = models.DateTimeField()

    class Meta:
        unique_together = ('identifier', 'user')
    
    def consume(self, num_tokens, save=True):
        """Remove num_tokens from the bucket.
        
        If there are not enough tokens available it will not remove any
        token but raise a TokensExceeded exception.
        
        It saves the state of the bucket to the database unless ``save``
        is set to False.
        """
        now = timezone.now()
        total_tokens = self._calc_tokens(now)
        wait_seconds = self.wait_seconds(num_tokens, total_tokens)
        if wait_seconds != 0:
            raise TokensExceeded(now + timedelta(seconds=wait_seconds))
        total_tokens -= num_tokens
        self.tokens = total_tokens
        self.last_updated = now
        if save:
            self.save()
    
    def wait_seconds(self, num_tokens, total_tokens=None):
        """Return the number of seconds to wait for ``num_tokens``.
        
        If no waiting is required 0 is returned.
        """
        if num_tokens > self.max_tokens:
            raise ValueError("The bucket capacity is too small.")
        
        if total_tokens is None:
            now = timezone.now()
            total_tokens = self._calc_tokens(now)

        if num_tokens <= total_tokens:
            return 0 
        num_missing = num_tokens-total_tokens
        return num_missing/self.fill_rate

    def _calc_tokens(self, now):
        delta = (now-self.last_updated).total_seconds()
        return min(self.tokens + delta*self.fill_rate, self.max_tokens)

    @classmethod
    def get(cls, identifier, user, max_tokens, fill_rate):
        """Get a token bucket with specified configuration.
        
        Always use this function to get a bucket!
        """
        try:
            return cls.objects.get(identifier=identifier, user=user)
        except cls.DoesNotExist:
            return cls(identifier=identifier,
                       user=user,
                       max_tokens=max_tokens,
                       fill_rate=fill_rate,
                       tokens=max_tokens,
                       last_updated=timezone.now())
