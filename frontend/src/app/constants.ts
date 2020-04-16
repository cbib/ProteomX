export class Constants
{
    static APIConfig = class
    {
        //static APIUrl:string = 'https://services.cbib.u-bordeaux.fr/ProteomiX:4000';
        static APIUrl:string = 'http://localhost:4000/';
	static get_api(){
            return this.APIUrl;
        }
    };

}
