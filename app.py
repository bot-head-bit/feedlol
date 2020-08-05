from flask import Flask, jsonify, request
import fetch as fch
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

fch.getData()


@app.route('/', methods=['GET'])
def root():

    if request.method == 'GET':

        finalResponse = {}
        finalResponse['api_source'] = 'https://github.com/aksty/parssfeed'
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        pretty = request.args.get('pretty')
        urlreq = request.args.get('url')
        page = request.args.get('page')
        query = request.args.get('q')

        if pretty is not None:
            if pretty == "1" or pretty.lower() == "true":
                app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        if page is None:
            page = -1
        else:
            page = int(page)
        if query is None:
            query = ""
        if urlreq is not None:
            finalResponse['feedResults'] = fch.specSource(urlreq, page, query, cacheflag=False)
            if len(finalResponse['feedResults']) == 0:
                finalResponse['feedResults'] = {'message': 'No results'}
                return jsonify(finalResponse), 404
            if 'error' in finalResponse['feedResults'].keys():
                return jsonify(finalResponse), 404
            return jsonify(finalResponse)
        finalResponse['feed_sources'] = fch.configs['sources']
        return jsonify(finalResponse)


@app.route('/<string:rt>', methods=['GET'])
def apiroute(rt):

    if request.method == 'GET':

        pretty = request.args.get('pretty')
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

        if pretty is not None:
            if pretty == "1" or pretty.lower() == "true":
                app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        if rt.strip() == "feed":
            finalResponse = {}
            finalResponse['api_source'] = 'https://github.com/aksty/parssfeed'
            finalResponse['feed_sources'] = fch.configs['sources']
            page = request.args.get('page')
            query = request.args.get('q')
            if page is None:
                page = 1
            else:
                page = int(page)
            ltst = "feed" if fch.configs['api_url'][-1] == '/' else "/feed"
            if query is not None:
                res = fch.searchFilter(fch.finallist, query)
                totalPages = int(len(res) / fch.configs['itemsPerPage'])
                mod = len(res) % fch.configs['itemsPerPage']
                if mod > 0:
                    totalPages = totalPages + 1
                finalResponse['totalPages'] = int(totalPages)
                finalResponse['next'] = fch.configs['api_url'] + ltst + '?page=' + str(page + 1) + '&q=' + query if int(
                    totalPages) > page else "end"
            else:
                res = fch.finallist
                totalPages = len(res) / fch.configs['itemsPerPage']
                mod = len(res) % fch.configs['itemsPerPage']
                if mod > 0:
                    totalPages = totalPages + 1
                finalResponse['totalPages'] = int(totalPages)
                finalResponse['next'] = fch.configs['api_url'] + ltst + '?page=' + str(page + 1) if int(
                    totalPages) > page else "end"
            startIndex = (page - 1) * fch.configs['itemsPerPage']
            finalResponse['feedResults'] = res[startIndex: startIndex + fch.configs['itemsPerPage']]
            if len(finalResponse['feedResults']) == 0:
                finalResponse['feedResults'] = {'message': 'No matching results'}
                return jsonify(finalResponse), 404
            return jsonify(finalResponse)
        elif rt.strip() in fch.configs['sources'].keys():
            finalResponse = dict()
            finalResponse['api_source'] = 'https://github.com/aksty/parssfeed'
            finalResponse['feed_sources'] = fch.configs['sources']
            page = request.args.get('page')
            query = request.args.get('q')
            sourceinfo = request.args.get('sourceinfo')
            if sourceinfo is not None:
                if sourceinfo == "1" or sourceinfo.lower() == "true":
                    finalResponse['source_info'] = fch.channelinfo(fch.configs['sources'][rt.strip()])
                    return jsonify(finalResponse)
            if page is None:
                page = -1
            else:
                page = int(page)
            if query is None:
                query = ""
            cacheflag = True if page == 1 or page == 2 or page == -1 else False
            res = fch.specSource(fch.configs['sources'][rt.strip()], page, query, cacheflag)
            finalResponse['feedResults'] = res
            finalResponse['source_info'] = fch.channelinfo(fch.configs['sources'][rt.strip()])
            if len(finalResponse['feedResults']) == 0:
                finalResponse['feedResults'] = {'message': 'No matching results'}
                return jsonify(finalResponse), 404
            return jsonify(finalResponse)
        else:
            return jsonify({'error': 'invalid request'}), 404


if __name__ == '__main__':
    app.run()
