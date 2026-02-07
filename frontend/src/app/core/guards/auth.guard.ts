import { inject } from '@angular/core';
import { Router, type CanActivateFn } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.accessToken()) {
    return router.createUrlTree(['/login']);
  }

  if (auth.currentUser()) {
    return true;
  }

  return auth.validateSession().pipe(
    map(user => (user ? true : router.createUrlTree(['/login']))),
    catchError(() => of(router.createUrlTree(['/login']))),
  );
};
