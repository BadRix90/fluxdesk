import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from '../services/auth.service';

const SKIP_URLS = ['/api/auth/token/', '/api/auth/token/refresh/'];

export const refreshTokenInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  if (SKIP_URLS.some(url => req.url.includes(url))) {
    return next(req);
  }

  return next(req).pipe(
    catchError(error => {
      if (error.status !== 401 || !auth.accessToken()) {
        return throwError(() => error);
      }

      return auth.refreshToken().pipe(
        switchMap(tokens => {
          const retryReq = req.clone({
            setHeaders: { Authorization: `Bearer ${tokens.access}` },
          });
          return next(retryReq);
        }),
        catchError(refreshError => {
          auth.logout();
          return throwError(() => refreshError);
        }),
      );
    }),
  );
};
