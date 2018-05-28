from celery import Celery

app = Celery('place',
             broker='amqp://',
             backend='rpc://',
             include='place.experiment')

if __name__ == '__main__':
    app.start()
