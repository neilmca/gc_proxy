import webapp2
import logging
import webapp2


class BaseHandler(webapp2.RequestHandler):


    def handle_exception(self, exception, debug):
        # Log the error.
        
        logging.info('log exception next')
        logging.exception(exception)

        # Set a custom message.
        self.response.write(exception)

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)

        else:
            self.response.set_status(500)
