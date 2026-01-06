import { Chat } from './components/Chat';
import { logger } from './utils/logger';

function App() {
  logger.info('CR360 Frontend initialized');

  return <Chat />;
}

export default App;
