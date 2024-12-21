export const getExpirationDate = (seconds: number): number => {
  const now = new Date();
  return (now.getTime() / 1000) + seconds;
};

export const isTokenExpired = (expiresIn: number): boolean => {
  return expiresIn <= Date.now() / 1000;
};
