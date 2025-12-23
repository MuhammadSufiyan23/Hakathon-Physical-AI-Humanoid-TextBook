import { PrismaClient } from '@prisma/client';

// In development, use a global instance to avoid hot reloading issues
const globalForPrisma = globalThis;

export const prisma = globalForPrisma.prisma || new PrismaClient({
  log: ['query', 'info', 'warn', 'error'],
});

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}