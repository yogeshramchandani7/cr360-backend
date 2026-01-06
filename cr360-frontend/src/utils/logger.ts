/**
 * Comprehensive logging utility for debugging
 * Logs to console with timestamps, context, and structured formatting
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  component?: string;
  action?: string;
  [key: string]: any;
}

class Logger {
  private isDevelopment = import.meta.env.DEV;

  private formatTimestamp(): string {
    return new Date().toISOString();
  }

  private formatMessage(level: LogLevel, message: string, context?: LogContext): void {
    const timestamp = this.formatTimestamp();
    const prefix = `[${timestamp}] [${level.toUpperCase()}]`;

    if (!this.isDevelopment && level === 'debug') {
      return; // Skip debug logs in production
    }

    const contextStr = context ? JSON.stringify(context, null, 2) : '';

    switch (level) {
      case 'debug':
        console.debug(prefix, message, contextStr);
        break;
      case 'info':
        console.info(prefix, message, contextStr);
        break;
      case 'warn':
        console.warn(prefix, message, contextStr);
        break;
      case 'error':
        console.error(prefix, message, contextStr);
        break;
    }
  }

  debug(message: string, context?: LogContext): void {
    this.formatMessage('debug', message, context);
  }

  info(message: string, context?: LogContext): void {
    this.formatMessage('info', message, context);
  }

  warn(message: string, context?: LogContext): void {
    this.formatMessage('warn', message, context);
  }

  error(message: string, error?: Error | any, context?: LogContext): void {
    const errorContext = {
      ...context,
      error: error instanceof Error ? {
        name: error.name,
        message: error.message,
        stack: error.stack,
      } : error,
    };
    this.formatMessage('error', message, errorContext);
  }

  // Specific logging methods for common operations
  apiRequest(method: string, url: string, payload?: any): void {
    this.debug('API Request', {
      component: 'API',
      action: 'request',
      method,
      url,
      payload,
    });
  }

  apiResponse(url: string, status: number, data?: any): void {
    this.debug('API Response', {
      component: 'API',
      action: 'response',
      url,
      status,
      data,
    });
  }

  apiError(url: string, error: any): void {
    this.error('API Error', error, {
      component: 'API',
      action: 'error',
      url,
    });
  }

  componentMount(componentName: string): void {
    this.debug(`Component mounted: ${componentName}`, {
      component: componentName,
      action: 'mount',
    });
  }

  componentUnmount(componentName: string): void {
    this.debug(`Component unmounted: ${componentName}`, {
      component: componentName,
      action: 'unmount',
    });
  }

  stateChange(componentName: string, stateName: string, oldValue: any, newValue: any): void {
    this.debug(`State changed: ${stateName}`, {
      component: componentName,
      action: 'state_change',
      stateName,
      oldValue,
      newValue,
    });
  }
}

// Export singleton instance
export const logger = new Logger();
